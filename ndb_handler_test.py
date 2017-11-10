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

"""Unit tests for ndb operations."""

import datetime
import unittest

import mock
from models import AppCredential
from models import AppUser
from ndb_handler import InitUser
from ndb_handler import RetrieveAppCredential
from ndb_handler import RevokeOldCredentials

from google.appengine.api import users
from google.appengine.ext import testbed


class NdbHandlerTest(unittest.TestCase):
  """Tests for ndb_handler.py."""

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

    self.existing_app_user = users.User('johndoe@gmail.com')
    AppUser(user=self.existing_app_user, email='johndoe@gmail.com').put()
    self.new_app_user = users.User('janedoe@gmail.com')

    AppUser.date_acquired._auto_now = False  # override for testing purposes

    self.old_user = users.User('olduser@gmail.com')
    AppUser(user=self.old_user, email='olduser@gmail.com',
            refresh_token='should not exist',
            date_acquired=datetime.datetime(2000, 1, 1)).put()

    AppUser.date_acquired._auto_now = True

    self.recent_user = users.User('newuser@gmail.com')
    AppUser(user=self.recent_user, email='newuser@gmail.com',
            refresh_token='should exist').put()

    app_credential = AppCredential(client_id='1', client_secret='secret')
    app_credential.put()

  def tearDown(self):
    self.testbed.deactivate()

  def testInitExistingUser(self):
    users.get_current_user = mock.MagicMock(return_value=self.existing_app_user)
    self.assertEqual(self.existing_app_user, InitUser().user)

  def testInitNewUser(self):
    users.get_current_user = mock.MagicMock(return_value=self.new_app_user)
    self.assertEqual(self.new_app_user, InitUser('new token').user)
    new_app_user_ndb = AppUser.query(
        AppUser.user == users.get_current_user()).fetch()[0]
    self.assertTrue(new_app_user_ndb)
    self.assertEqual('new token', new_app_user_ndb.refresh_token)

  def testAppCredential(self):
    client_id, client_secret = RetrieveAppCredential()
    self.assertEqual('1', client_id)
    self.assertEqual('secret', client_secret)

  def testRevokeOldUserCredentials(self):
    users.get_current_user = mock.MagicMock(return_value=self.old_user)
    RevokeOldCredentials()
    user_ndb = InitUser()
    self.assertEqual(None, user_ndb.refresh_token)

  def testNotRevokeNewUserCredentials(self):
    users.get_current_user = mock.MagicMock(return_value=self.recent_user)
    RevokeOldCredentials()
    user_ndb = InitUser()
    self.assertTrue(user_ndb.refresh_token)

if __name__ == '__main__':
  unittest.main()
