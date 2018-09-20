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

"""AppEngine application WSGI entry point.

Configures the web application that will display the DFP Playground UI.
"""

import os
import sys

# Prepend lib directory that contains third-party libraries to the system path
sys.path.insert(0, os.path.join(os.path.abspath('.'), 'lib'))

from views import APIViewHandler
from views import Login
from views import LoginCallback
from views import LoginErrorPage
from views import MainPage
from views import MakeTestNetworkPage
from views import PutCredentials
from views import RevokeOldRefreshTokens
import webapp2

VERSION = '1.0.8'

app = webapp2.WSGIApplication(
    [
        webapp2.Route('/', MainPage),
        webapp2.Route('/login', Login),
        webapp2.Route('/oauth2callback', LoginCallback),
        webapp2.Route('/login/error', LoginErrorPage),
        webapp2.Route('/tasks/revoke', RevokeOldRefreshTokens),
        webapp2.Route('/make-test-network', MakeTestNetworkPage),
        webapp2.Route('/api/<method>', handler=APIViewHandler),
        webapp2.Route('/tasks/put-credentials', PutCredentials)
    ],
    debug=True)
