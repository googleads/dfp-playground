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

"""Module for data models used in the DFP Playground."""

from google.appengine.ext import ndb


class AppUser(ndb.Model):
  """Implements AppUser.

  The AppUser represents an API user in a datastore. For each user, we store
  their email address and refresh token credentials.
  """
  user = ndb.UserProperty(required=True)
  email = ndb.StringProperty(required=True)
  refresh_token = ndb.StringProperty(required=False)
  date_acquired = ndb.DateTimeProperty(auto_now=True)



class AppCredential(ndb.Model):
  """Implements AppCredential.

  The AppCredential is a dummy class that accesses the application's client
  customer id and the client customer secret. There should only be exactly
  one such entity of this kind in the application's datastore.
  """
  client_id = ndb.StringProperty(required=True)
  client_secret = ndb.StringProperty(required=True)
