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

"""Handlers to make calls against the DoubleClick for Publishers (DFP) API."""

from httplib import HTTPException

from googleads.dfp import DfpClient
from googleads.dfp import FilterStatement
from googleads.oauth2 import GoogleRefreshTokenClient
from utils import retry


class APIHandler(object):
  """Handler for the DFP API using the DFP Client Libraries."""

  def __init__(self, client_id, client_secret, refresh_token, application_name):
    """Initializes an APIHandler.

    Args:
      client_id: The client id retrieved from the Cloud Console.
      client_secret: The client secret retrieved from the Cloud Console.
      refresh_token: The user's refresh token retrieved from Datastore.
      application_name: The name of the AppEngine application.
    """
    credentials = GoogleRefreshTokenClient(client_id, client_secret,
                                           refresh_token)
    self.client = DfpClient(credentials, application_name)
    self.page_limit = 25

  @retry(HTTPException)
  def GetAllNetworks(self):
    """Retrieves the user's available networks.

    Returns:
      list List of Network data objects.
    """
    network_service = self.client.GetService('NetworkService')
    networks = network_service.getAllNetworks()
    return {
        'results': networks,
        'totalResultSetSize': len(networks),
    }

  @retry(HTTPException)
  def MakeTestNetwork(self):
    """Makes a new test network.

    Returns:
      Network A network object.
    """
    network_service = self.client.GetService('NetworkService')
    return network_service.makeTestNetwork()

  @retry(HTTPException)
  def GetUsers(self, network_code, statement=None):
    """Returns users in the network specified by network_code.

    Args:
      network_code: str Network code to use when looking up users.
      statement: FilterStatement PQL Statement to filter results.
                 Defaults to None.

    Returns:
      dict Dict including a list of User data objects and total set size.
    """
    user_service = self.client.GetService('UserService')
    return self._GetLimitedResults(user_service.getUsersByStatement,
                                   network_code, statement)

  @retry(HTTPException)
  def GetAdUnits(self, network_code, statement=None):
    """Returns ad units in the network specified by network_code.

    Args:
      network_code: str Network code to use when looking up ad units.
      statement: FilterStatement PQL Statement to filter results.
                 Defaults to None.

    Returns:
      dict Dict including a list of AdUnit data objects and total set size.
    """
    inventory_service = self.client.GetService('InventoryService')
    return self._GetLimitedResults(inventory_service.getAdUnitsByStatement,
                                   network_code, statement)

  @retry(HTTPException)
  def GetCompanies(self, network_code, statement=None):
    """Returns companies in the network specified by network_code.

    Args:
      network_code: str Network code to use when looking up companies.
      statement: FilterStatement PQL Statement to filter results.
                 Defaults to None.

    Returns:
      dict Dict including a list of Company data objects and total set size.
    """
    company_service = self.client.GetService('CompanyService')
    return self._GetLimitedResults(company_service.getCompaniesByStatement,
                                   network_code, statement)

  @retry(HTTPException)
  def GetCreatives(self, network_code, statement=None):
    """Returns creatives in the network specified by network_code.

    Args:
      network_code: str Network code to use when looking up creatives.
      statement: FilterStatement PQL Statement to filter results.
                 Defaults to None.

    Returns:
      dict Dict including a list of Creative data objects and total set size.
    """
    creative_service = self.client.GetService('CreativeService')
    return self._GetLimitedResults(creative_service.getCreativesByStatement,
                                   network_code, statement)

  @retry(HTTPException)
  def GetCreativeTemplates(self, network_code, statement=None):
    """Returns creative templates in the network specified by network_code.

    Args:
      network_code: str Network code to use when looking up creative templates.
      statement: FilterStatement PQL Statement to filter results.
                 Defaults to None.

    Returns:
      dict Dict including a list of Creative Template data objects and total
      set size.
    """
    creative_template_service = self.client.GetService(
        'CreativeTemplateService')
    return self._GetLimitedResults(
        creative_template_service.getCreativeTemplatesByStatement, network_code,
        statement)

  @retry(HTTPException)
  def GetCustomTargetingKeys(self, network_code, statement=None):
    """Returns custom targeting keys in the network specified by network_code.

    Args:
      network_code: str Network code to use when looking up custom targeting.
      statement: FilterStatement PQL Statement to filter results.
                 Defaults to None.

    Returns:
      dict Dict including a list of Custom Targeting data objects and total
      set size.
    """
    custom_targeting_service = self.client.GetService('CustomTargetingService')
    return self._GetLimitedResults(
        custom_targeting_service.getCustomTargetingKeysByStatement,
        network_code, statement)

  @retry(HTTPException)
  def GetCustomTargetingValues(self, network_code, statement=None):
    """Returns custom targeting values in the network specified by network_code.

    Args:
      network_code: str Network code to use when looking up custom targeting.
      statement: FilterStatement PQL Statement to filter results.
                 Defaults to None.

    Returns:
      dict Dict including a list of Custom Targeting data objects and total
      set size.
    """
    custom_targeting_service = self.client.GetService('CustomTargetingService')
    return self._GetLimitedResults(
        custom_targeting_service.getCustomTargetingValuesByStatement,
        network_code, statement)

  @retry(HTTPException)
  def GetLICAs(self, network_code, statement=None):
    """Returns LICAs in the network specified by network_code.

    Args:
      network_code: str Network code to use when looking up LICAs.
      statement: FilterStatement PQL Statement to filter results.
                 Defaults to None.

    Returns:
      dict Dict including a list of LICA data objects and total set size.
    """
    lica_service = self.client.GetService('LineItemCreativeAssociationService')
    return self._GetLimitedResults(
        lica_service.getLineItemCreativeAssociationsByStatement, network_code,
        statement)

  @retry(HTTPException)
  def GetOrders(self, network_code, statement=None):
    """Returns orders in the network specified by network_code.

    Args:
      network_code: str Network code to use when looking up orders.
      statement: FilterStatement PQL Statement to filter results.
                 Defaults to None.

    Returns:
      dict Dict including a list of Order data objects and total set size.
    """
    order_service = self.client.GetService('OrderService')
    return self._GetLimitedResults(order_service.getOrdersByStatement,
                                   network_code, statement)

  @retry(HTTPException)
  def GetLineItems(self, network_code, statement=None):
    """Returns line items in the network specified by network_code.

    Args:
      network_code: str Network code to use when looking up line items.
      statement: FilterStatement PQL Statement to filter results.
                 Defaults to None.

    Returns:
      dict Dict including a list of Line Item data objects and total set size.
    """
    line_item_service = self.client.GetService('LineItemService')
    return self._GetLimitedResults(line_item_service.getLineItemsByStatement,
                                   network_code, statement)

  @retry(HTTPException)
  def GetPlacements(self, network_code, statement=None):
    """Returns placements in the network specified by network_code.

    Args:
      network_code: str Network code to use when looking up placements.
      statement: FilterStatement PQL Statement to filter results.
                 Defaults to None.

    Returns:
      dict Dict including a list of Placement data objects and total set size.
    """
    placement_service = self.client.GetService('PlacementService')
    return self._GetLimitedResults(placement_service.getPlacementsByStatement,
                                   network_code, statement)

  @retry(HTTPException)
  def GetPQLSelection(self, network_code, statement):
    """Returns rows in the network that match the statement.

    Args:
      network_code: str Network code to use when looking up placements.
      statement: FilterStatement PQL Statement to filter through rows.

    Returns:
      dict Dict including a list of Row objects and total set size.
    """
    pql_service = self.client.GetService('PublisherQueryLanguageService')
    return self._GetLimitedResults(pql_service.select, network_code, statement,
                                   True)

  def _GetLimitedResults(self,
                         getter_func,
                         network_code=None,
                         statement=None,
                         is_pql_result=False):
    """Returns up to 25 entities given a getter_func.

    The set of users returned can be altered by specifying a statement with
    an offset or a limit less than 25.

    Args:
      getter_func: func Function to retrieve results from a service.
      network_code: str Network code to use when interacting with the service.
                    Defaults to None.
      statement: FilterStatement PQL Statement to filter results.
                 Defaults to None.
      is_pql_result: The response from the DFP API is coming from the
                     PQL Service and will only include the results.
                     Defaults to False.

    Returns:
      dict Dict including a list of data objects and total set size.
    """
    self.client.network_code = network_code
    if statement:
      statement.limit = min(statement.limit, self.page_limit)
    else:
      statement = FilterStatement(limit=self.page_limit)
    response = getter_func(statement.ToStatement())
    if is_pql_result:
      return {
          'results': response['rows'] if 'rows' in response else [],
          'columns': [
              column['labelName'] for column in response['columnTypes']
          ],
      }

    total_result_set_size = response['totalResultSetSize']
    results = response['results'] if total_result_set_size > 0 else []
    return {
        'results': results,
        'totalResultSetSize': total_result_set_size,
    }
