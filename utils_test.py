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

"""Tests for utils used in the DFP Playground."""

import logging
import unittest

import mock
from models import AppCredential
from models import AppUser
import suds.sudsobject
from utils import oauth2required
from utils import retry
from utils import unpack_row
from utils import unpack_suds_object

from google.appengine.api import users
from google.appengine.ext import testbed


class UtilsTest(unittest.TestCase):
  """Tests for utils.py."""

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

    app_credential = AppCredential(client_id='1', client_secret='secret')
    app_credential.put()

    self.new_app_user = users.User('johndoe@gmail.com')
    self.existing_app_user = users.User('janedoe@gmail.com')
    AppUser(user=self.existing_app_user, email='janedoe@gmail.com',
            refresh_token='blah').put()

    # mocking webapp2 request object
    class RequestMock(object):

      def redirect(self, uri):
        return uri

    self.request_mock = RequestMock()

    # mocking handler
    @oauth2required
    def homepage_mock(request):
      return '/'
    self.homepage_mock = homepage_mock

    # helper class for mocking retry decorator
    class TestObject(object):

      def __init__(test_self):
        test_self.fails_remaining = 2

      @retry(NotImplementedError)
      def instant_success_func(test_self):
        return 'success'

      @retry(NotImplementedError)
      def eventual_success_func(test_self):
        if test_self.fails_remaining > 0:
          test_self.fails_remaining -= 1
          raise NotImplementedError()
        return 'success'

      @retry(NotImplementedError)
      def failure_func(test_self):
        raise NotImplementedError()

    self.test_obj = TestObject()
    logging.warning = mock.MagicMock(side_effect=logging.warning)

    # simulating a line item object
    self.suds_obj = suds.sudsobject.Object()
    self.suds_obj.goal = suds.sudsobject.Object()
    self.suds_obj.goal.units = 10000
    self.suds_obj.goal.goalType = 'LIFETIME'
    self.suds_obj.goal.unitType = 'IMPRESSIONS'
    self.suds_obj.orderId = 987654321
    self.suds_obj.endDateTime = suds.sudsobject.Object()
    self.suds_obj.endDateTime.date = suds.sudsobject.Object()
    self.suds_obj.endDateTime.date.year = 2015
    self.suds_obj.endDateTime.date.day = 31
    self.suds_obj.endDateTime.date.month = 12
    self.suds_obj.endDateTime.timeZoneID = 'America/New_York'
    self.suds_obj.endDateTime.second = 0
    self.suds_obj.endDateTime.hour = 23
    self.suds_obj.endDateTime.minute = 59
    self.suds_obj.reserveAtCreation = False

    def create_suds_test_obj(id_):
      obj = suds.sudsobject.Object()
      obj.id = id_
      obj.type = 'PIXEL'
      return obj
    self.suds_obj.creativePlaceholders = [
        create_suds_test_obj(0),
        create_suds_test_obj(1),
        create_suds_test_obj(2),
    ]

    self.unpacked_suds_obj = {
        'goal': {
            'units': 10000,
            'goalType': 'LIFETIME',
            'unitType': 'IMPRESSIONS',
        },
        'orderId': 987654321,
        'endDateTime': {
            'date': {
                'year': 2015,
                'day': 31,
                'month': 12,
            },
            'timeZoneID': 'America/New_York',
            'second': 0,
            'hour': 23,
            'minute': 59,
        },
        'reserveAtCreation': False,
        'creativePlaceholders': [
            {
                'id': 0,
                'type': 'PIXEL',
            },
            {
                'id': 1,
                'type': 'PIXEL',
            },
            {
                'id': 2,
                'type': 'PIXEL',
            },
        ],
    }

    # simulating a row object from PQLService
    self.cols = ['id', 'browsername']
    self.row_obj = suds.sudsobject.Object()
    self.row_obj.values = [
        suds.sudsobject.Object(),
        suds.sudsobject.Object(),
    ]
    self.row_obj.values[0].value = '123456'
    self.row_obj.values[1].value = 'Test Browser'
    self.unpacked_row_obj = {
        'id': '123456',
        'browsername': 'Test Browser',
    }

  def tearDown(self):
    self.testbed.deactivate()

  def testOauth2RedirectForNewUser(self):
    users.get_current_user = mock.MagicMock(return_value=self.new_app_user)
    self.assertEqual('/login', self.homepage_mock(self.request_mock))

  def testOauth2RedirectForExistingUser(self):
    users.get_current_user = mock.MagicMock(return_value=self.existing_app_user)
    self.assertEqual('/', self.homepage_mock(self.request_mock))

  def testEventualSuccess(self):
    self.assertEqual('success', self.test_obj.eventual_success_func())
    self.assertEqual(2, logging.warning.call_count)

  def testFailure(self):
    self.assertRaises(RuntimeError, self.test_obj.failure_func)
    self.assertEqual(3, logging.warning.call_count)

  def testInstantSuccess(self):
    self.assertEqual('success', self.test_obj.instant_success_func())
    self.assertEqual(0, logging.warning.call_count)

  def testUnpackEmptyObject(self):
    empty_obj = suds.sudsobject.Object()
    self.assertEqual({}, unpack_suds_object(empty_obj))

  def testUnpackObject(self):
    self.assertEqual(self.unpacked_suds_obj, unpack_suds_object(self.suds_obj))

  def testUnpackEmptyRow(self):
    empty_row = suds.sudsobject.Object()
    self.assertEqual({}, unpack_row(empty_row, self.cols))

  def testUnpackRow(self):
    self.assertEqual(self.unpacked_row_obj, unpack_row(self.row_obj, self.cols))


if __name__ == '__main__':
  unittest.main()
