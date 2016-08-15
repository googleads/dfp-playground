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
"""Utilities for the DFP Playground Webapp."""

from functools import wraps
import logging

from ndb_handler import InitUser
from suds.sudsobject import asdict


def oauth2required(view_func):
  """Decorator to require OAuth2 credentials for a view.

  If credentials (a valid refresh token) are not available for the current
  user, then they will be redirected to the authorization flow.

  Args:
    view_func: func The original request view function.

  Returns:
    func The decorator function.
  """

  @wraps(view_func)
  def check_dfp_credentials_exist(request, *args, **kwargs):
    """The decorator function.

    Args:
      request: Request The webapp2 request object.
      *args: Additional args.
      **kwargs: Additional kwargs.

    Returns:
      func The decorator function.
    """
    # check if user's refresh token exists
    user_ndb = InitUser()
    if user_ndb.refresh_token:
      # Refresh token already exists in database. Proceed to homepage.
      return view_func(request, *args, **kwargs)

    # Refresh token doesn't exist.
    # Proceed to step 1: Redirecting to authorization server.
    return request.redirect('/login')

  return check_dfp_credentials_exist


def retry(exception_to_check, attempts=3):
  """Decorator to retry a function upon exception.

  If the decorated function emits an exception that matches exception_to_check,
  the function will be repeated. This will happen a maximum of 'attempts' times.
  If none of the attempts were successful, this function raises a RuntimeError.

  Args:
    exception_to_check: Exception An Exception or a tuple of Exceptions.
    attempts: int Number of attempts to retry.

  Returns:
    func The decorator function.

  Raises:
    RuntimeError: Error once all attempts have been exhausted.
  """

  def decorator_wrap(func):
    """The decorator wrapper function.

    Args:
      func: func The original function.

    Returns:
      func The decorator function.

    Raises:
      RuntimeError: Error once all attempts have been exhausted.
    """

    @wraps(func)
    def retry_func(*args, **kwargs):
      """The decorator function.

      Args:
        *args: Additional args.
        **kwargs: Additional kwargs.

      Returns:
        func The decorator function.

      Raises:
        RuntimeError: Error once all attempts have been exhausted.
      """
      attempts_remaining = attempts
      while attempts_remaining > 0:
        try:
          return func(*args, **kwargs)
        except exception_to_check, e:
          attempts_remaining -= 1
          logging.warning('%s, Attempts remaining: %d', e, attempts_remaining)

      logging.error('Failed to execute %s after %d attempts', func.__name__,
                    attempts)
      raise RuntimeError('Failed to execute %s after %d attempts' %
                         (func.__name__, attempts))

    return retry_func

  return decorator_wrap


def unpack_suds_object(d):
  """Convert suds object into serializable format.

  Transform suds object received from the DFP API into a Python dict.

  Args:
    d: A suds object.

  Returns:
    dict A serializable Python dict.
  """
  out = {}
  for k, v in asdict(d).iteritems():
    if hasattr(v, '__keylist__'):
      out[k] = unpack_suds_object(v)
    elif isinstance(v, list):
      out[k] = []
      for item in v:
        if hasattr(item, '__keylist__'):
          out[k].append(unpack_suds_object(item))
        else:
          out[k].append(item)
    else:
      out[k] = v
  return out


def unpack_row(row, cols):
  """Convert a Row suds object into serializable format.

  Transform a row of results objects received from the DFP API's
  Publisher Query Language Service into a Python dict.

  Args:
    row: A row of suds object which include an array of values.
    cols: An array of strings representing the column names.

  Returns:
    dict A serializable Python dict.
  """
  try:
    # throws AttributeError is 'values' does not exist in row object
    values = map(lambda value: value['value'], row['values'])
    return dict(zip(cols, values))
  except AttributeError:
    return {}
