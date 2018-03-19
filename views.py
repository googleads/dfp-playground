# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""View handlers for the DFP Playground."""

import json
import logging
import os
import socket

from api_handler import APIHandler
from googleads import dfp
from googleads import oauth2
import jinja2
from ndb_handler import InitUser
from ndb_handler import ReplaceAppCredential
from ndb_handler import RetrieveAppCredential
from ndb_handler import RevokeOldCredentials
from oauth2client import client
from utils import oauth2required
from utils import unpack_row
from utils import unpack_suds_object
import webapp2

from google.appengine.api import app_identity
from google.appengine.api import users

_APPLICATION_NAME = 'DFP Playground'

# load templates
_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates')
_JINJA_ENVIRONMENT = jinja2.Environment(
    autoescape=True,
    extensions=['jinja2.ext.autoescape'],
    loader=jinja2.FileSystemLoader(_TEMPLATES_PATH))

_CLIENT_ID, _CLIENT_SECRET = RetrieveAppCredential()

# set timeout to 10 s
socket.setdefaulttimeout(10)

# initialize flow object
_HOSTNAME = app_identity.get_default_version_hostname()
_FLOW = client.OAuth2WebServerFlow(
    client_id=_CLIENT_ID,
    client_secret=_CLIENT_SECRET,
    scope=oauth2.GetAPIScope('dfp'),
    user_agent='DFP Playground',
    redirect_uri=(
        ('https://' + _HOSTNAME) if _HOSTNAME else 'http://localhost:8008') +
    '/oauth2callback',
    access_type='offline',
    approval_prompt='force')


class MainPage(webapp2.RequestHandler):
  """View that displays the DFP Playground's homepage."""

  @oauth2required
  def get(self):
    """Handle get request."""
    user = users.get_current_user()
    user_email = user.email()
    logout_url = users.create_logout_url('/')
    user_ndb = InitUser()

    template = _JINJA_ENVIRONMENT.get_template('index_page.html')
    self.response.write(
        template.render({
            'user_email': user_email,
            'logout_url': logout_url,
        }))


class Login(webapp2.RequestHandler):
  """View that redirects to the auth flow's first step."""

  def get(self):
    """Handle get request."""
    auth_uri = _FLOW.step1_get_authorize_url()
    self.redirect(auth_uri)


class LoginCallback(webapp2.RequestHandler):
  """View that handles the auth flow's callback, which contains credentials."""

  def get(self):
    """Handle get request."""
    if not self.request.get('code'):
      # User denied OAuth2 permissions.
      logging.info('User denied OAuth2 permissions')
      return self.redirect('/login/error')

    credentials = _FLOW.step2_exchange(self.request.get('code'))
    if credentials:
      # store user's credentials in database
      user_ndb = InitUser(credentials.refresh_token)

      # check if user has any networks
      api_handler = APIHandler(
          _CLIENT_ID, _CLIENT_SECRET, user_ndb, _APPLICATION_NAME)
      networks = api_handler.GetAllNetworks()
      if not networks:
        # if user has no networks, redirect to ask if one should be made
        return self.redirect('/make-test-network')
      return self.redirect('/')
    else:
      # failure: no credentials
      logging.error('No credentials found from step 2 in flow')
      return self.redirect('/login/error')


class LoginErrorPage(webapp2.RequestHandler):
  """View that notifies the user of a login failure."""

  def get(self):
    """Handle get request."""
    self.response.write('''
      Failed to log in. <a href="/login">Click</a> to try again.
      ''')


class MakeTestNetworkPage(webapp2.RequestHandler):
  """View that asks a new user to make a test network."""

  def get(self):
    """Handle get request."""
    template = _JINJA_ENVIRONMENT.get_template('make_network_page.html')
    self.response.write(template.render({}))


class APIViewHandler(webapp2.RequestHandler):
  """View that chooses the appropriate handler depending on the method."""
  api_handler_method_map = {
      'users': 'GetUsers',
      'adunits': 'GetAdUnits',
      'companies': 'GetCompanies',
      'creatives': 'GetCreatives',
      'creativetemplates': 'GetCreativeTemplates',
      'customtargetingkeys': 'GetCustomTargetingKeys',
      'customtargetingvalues': 'GetCustomTargetingValues',
      'licas': 'GetLICAs',
      'orders': 'GetOrders',
      'lineitems': 'GetLineItems',
      'placements': 'GetPlacements',
      'pql': 'GetPQLSelection',
  }

  def get(self, method):
    """Delegate GET request calls to the DFP API."""
    method = method.lower()
    user_ndb = InitUser()
    api_handler = APIHandler(
        _CLIENT_ID, _CLIENT_SECRET, user_ndb, _APPLICATION_NAME)
    network_code = self.request.get('network_code')

    # parse parameters
    try:
      limit = int(self.request.get('limit', api_handler.page_limit))
    except ValueError:
      self.response.status = 400
      return self.response.write('Limit must be an integer')
    try:
      offset = int(self.request.get('offset', 0))
    except ValueError:
      self.response.status = 400
      return self.response.write('Offset must be an integer')

    if method == 'networks':
      return_obj = api_handler.GetAllNetworks()
    else:
      # construct PQL statement
      where_clause = self.request.get('where', '')
      statement = dfp.FilterStatement(where_clause, limit=limit, offset=offset)

      try:
        # throws KeyError if method not found
        api_handler_func = getattr(api_handler,
                                   self.api_handler_method_map[method])
      except KeyError:
        self.response.status = 400
        self.response.write('API method not supported (%s).' % method)

      # retrieve return_obj from api_handler and modify it
      return_obj = api_handler_func(network_code, statement)

    # process return_obj
    if 'columns' in return_obj:
      # special case: return_obj is from PQL Service
      cols = return_obj['columns']
      return_obj['results'] = [
          unpack_row(row, cols) for row in return_obj['results']
      ]
    else:
      # regular case
      return_obj['results'] = [
          unpack_suds_object(obj) for obj in return_obj['results']
      ]

    if self.request.get('limit'):
      return_obj['limit'] = limit
    else:
      try:
        return_obj['limit'] = return_obj['totalResultSetSize']
      except KeyError:
        return_obj['limit'] = api_handler.page_limit
    return_obj['offset'] = offset

    # construct response headers
    self.response.headers['Content-Type'] = 'application/json'

    self.response.write(json.dumps(return_obj))

  def post(self, method):
    """Delegate POST request calls to the DFP API."""
    if method == 'networks':
      user_ndb = InitUser()
      api_handler = APIHandler(
          _CLIENT_ID, _CLIENT_SECRET, user_ndb, _APPLICATION_NAME)
      api_handler.MakeTestNetwork()
      return self.redirect('/')
    else:
      self.response.status = 400
      self.response.write(method + ' API POST method not found.')


class RevokeOldRefreshTokens(webapp2.RequestHandler):
  """View that revokes old credentials. It is used in cron.yaml."""

  def get(self):
    """Handle get request."""
    if self.request.headers.get('X-Appengine-Cron'):
      RevokeOldCredentials()
    else:
      self.response.status = 401


class PutCredentials(webapp2.RequestHandler):
  """View that allows an admin user to replace credentials."""

  def get(self):
    template = _JINJA_ENVIRONMENT.get_template('create_credentials.html')
    self.response.write(template.render())

  def post(self):
    client_id = self.request.POST['client_id']
    client_secret = self.request.POST['client_secret']

    ReplaceAppCredential(client_id, client_secret)

    self.response.write(
        'Success! Restart the server to load these credentials.')
