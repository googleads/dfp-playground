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
"""Handlers for ndb operations."""

import datetime
import logging
from models import AppCredential
from models import AppUser

from google.appengine.api import users
from google.appengine.api.datastore_errors import BadArgumentError
from google.appengine.ext import ndb


def InitUser(refresh_token=None):
  """Initialize application user.

  Retrieve existing user credentials from datastore or add new user.
  If a refresh token is specified, it replaces the old refresh token and the
  date_acquired is updated as well.

  Args:
    refresh_token: str A new refresh token received from the auth flow.
                   Defaults to None.

  Returns:
    AppUser instance of the application user.
  """
  result = AppUser.query(
      AppUser.user == users.get_current_user()).fetch(limit=1)

  if result:
    # app_user exists
    app_user = result[0]
    if not app_user.refresh_token:
      # update refresh_token if provided in the arguments
      app_user.refresh_token = refresh_token
      app_user.date_acquired = datetime.datetime.now()
  else:
    app_user = AppUser(
        user=users.get_current_user(),
        email=users.get_current_user().email(),
        refresh_token=refresh_token)

  app_user.put()
  return app_user


def RevokeOldCredentials():
  """Revoke old credentials.

  Find all users in the datastore with refresh tokens older than 30 days and
  revokes them.
  """
  users_with_expired_tokens = AppUser.query(
      AppUser.date_acquired <=
      datetime.datetime.now() - datetime.timedelta(30)).fetch()
  for expired_user in users_with_expired_tokens:
    expired_user.refresh_token = None
  ndb.put_multi(users_with_expired_tokens)


def RetrieveAppCredential():
  """Retrieve app credential.

  Retrieve the client id and the client secret from the
  application's datastore.

  Returns:
    tuple A tuple of (client id, client secret)
  """
  try:
    app_credential = AppCredential.query().fetch(limit=1)[0]
    return (app_credential.client_id, app_credential.client_secret)
  except BadArgumentError, e:
    # allow opensource test cases to run
    logging.warning('Could not retrieve AppCredential: %s', e)
    logging.warning('Disregard if you are running tests')
    return (None, None)
