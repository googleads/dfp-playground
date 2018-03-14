var app =
    angular.module('dfpPlayground', ['ngMaterial', 'ngMessages', 'ngSanitize']);

app.config(function($interpolateProvider, $mdThemingProvider) {
  $mdThemingProvider.theme('default').primaryPalette('green').accentPalette(
      'lime');
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
});

// Share networkCode among different controllers
app.factory('networkInfo', function() {
  var networkInfo = {networks: null, code: ''};
  return networkInfo;
});

app.controller('networkCtrl', function($scope, $http, networkInfo) {
  $scope.networkInfo = networkInfo;

  $scope.loadNetworks = function() {
    if ($scope.networkInfo.networks) {
      // networks have already been loaded
      return null;
    }
    return $http.get('/api/networks').then(function(response) {
      $scope.networkInfo.networks = response.data.results;
      // autoselect first network
      if ($scope.networkInfo.networks.length) {
        $scope.networkInfo.code = $scope.networkInfo.networks[0].networkCode;
      }
    });
  };

  // load networks immediately
  $scope.loadNetworks();
});

app.controller(
    'tabsCtrl',
    function(
        $scope, $http, $httpParamSerializer, $mdDialog, $timeout, networkInfo) {
      $scope.networkInfo = networkInfo;
      $scope.tabs = [];
      $scope.selectedIndex = 0;
      var selected = null;
      var previous = null;

      var constructDocsURL = function(servicePath) {
        var currentVersion = 'v201708';
        return (
            'https://developers.google.com/doubleclick-publishers/' +
            'docs/reference/' + currentVersion + '/' + servicePath);
      };
      $scope.availableServices = [
        {
          name: 'Ad Unit Service',
          route: 'adunits',
          displayattr: 'name',
          displayattrname: 'Name',
          defaultWhereClause: 'WHERE id != 0',
          docsinfo: constructDocsURL('InventoryService')
        },
        {
          name: 'Company Service',
          route: 'companies',
          displayattr: 'name',
          displayattrname: 'Name',
          defaultWhereClause: 'WHERE id != 0',
          docsinfo: constructDocsURL('CompanyService')
        },
        {
          name: 'Creative Service',
          route: 'creatives',
          displayattr: 'name',
          displayattrname: 'Name',
          defaultWhereClause: 'WHERE id != 0',
          docsinfo: constructDocsURL('CreativeService')
        },
        {
          name: 'Creative Template Service',
          route: 'creativetemplates',
          displayattr: 'name',
          displayattrname: 'Name',
          defaultWhereClause: 'WHERE id != 0',
          docsinfo: constructDocsURL('CreativeTemplateService')
        },
        {
          name: 'Custom Targeting Service',
          routes: [
            {
              route: 'customtargetingkeys',
              name: 'Key',
              defaultWhereClause: 'WHERE id != 0'
            },
            {
              route: 'customtargetingvalues',
              name: 'Value',
              defaultWhereClause: 'WHERE customTargetingKeyId != 0'
            }
          ],
          customfunc: function(newTab) {
            $scope.$watch(
                function() { return newTab.route; },
                function(newRoute, oldRoute) {
                  if (newRoute !== oldRoute) {
                    if (newRoute === 'customtargetingvalues') {
                      newTab.whereClause = 'WHERE customTargetingKeyId != 0';
                    } else {
                      newTab.whereClause = 'WHERE id != 0';
                    }
                  }
                });
          },
          displayattr: 'name',
          displayattrname: 'Name',
          docsinfo: constructDocsURL('CustomTargetingService')
        },
        {
          name: 'Line Item Service',
          route: 'lineitems',
          displayattr: 'name',
          displayattrname: 'Name',
          defaultWhereClause: 'WHERE id != 0',
          docsinfo: constructDocsURL('LineItemService')
        },
        {
          name: 'Line Item Creative Association Service',
          route: 'licas',
          displayattr: 'lineItemId',
          displayattrname: 'Line Item ID',
          defaultWhereClause: 'WHERE lineItemId != 0',
          docsinfo: constructDocsURL('LineItemCreativeAssociationService')
        },
        {
          name: 'Order Service',
          route: 'orders',
          displayattr: 'name',
          displayattrname: 'Name',
          defaultWhereClause: 'WHERE id != 0',
          docsinfo: constructDocsURL('OrderService')
        },
        {
          name: 'Placement Service',
          route: 'placements',
          displayattr: 'name',
          displayattrname: 'Name',
          defaultWhereClause: 'WHERE id != 0',
          docsinfo: constructDocsURL('PlacementService')
        },
        {
          name: 'PQL Service',
          route: 'pql',
          defaultWhereClause: 'SELECT Id, BrowserName from Browser',
          docsinfo: constructDocsURL('PublisherQueryLanguageService')
        },
        {
          name: 'User Service',
          route: 'users',
          displayattr: 'email',
          displayattrname: 'Email',
          defaultWhereClause: 'WHERE id != 0',
          docsinfo: constructDocsURL('UserService')
        }
      ];

      $scope.whereClause = null;
      $scope.limit = 100;
      $scope.offset = 0;

      $scope.$watch('selectedIndex', function(current, old) {
        previous = selected;
        selected = $scope.tabs[current];
      });

      var addTab = function(service) {
        var newTab = {
          title: service.name,
          route: service.route,
          routes: service.routes,
          displayattr: service.displayattr,
          displayattrname: service.displayattrname,
          docsinfo: service.docsinfo,
          loading: false,
          errormsg: '',
          pagination: {}
        };
        $scope.tabs.push(newTab);
        newTab.whereClause = (service.defaultWhereClause || 'WHERE id != 0');

        // custom logic
        if (newTab.customfunc) {
          newTab.customfunc();
        }
      };

      // load service tabs immediately
      var loadTabs = function() {
        var len = $scope.availableServices.length;
        for (var i = 0; i < len; i++) {
          addTab($scope.availableServices[i]);
        }
      };
      loadTabs();

      $scope.resetTab = function(tab) {
        tab.loading = false;
        tab.errormsg = '';
        tab.results = [];
        tab.columns = null;  // because !!null is false
        tab.empty = false;
      };

      $scope.resetPages = function(tab) {
        tab.pages = [];
        tab.pageNum = 1;
      };

      $scope.makeNewRequest = function(route, whereClause, limit, offset) {
        var params = {
          where: whereClause,
          limit: limit,
          offset: offset,
          network_code: networkInfo.code,
        };
        var qs = $httpParamSerializer(params);

        var uri = '/api/' + route + '?' + qs;

        var tab = $scope.tabs[$scope.selectedIndex];
        $scope.resetPages(tab);
        $scope.callAPI(uri, tab, function(response) {
          tab.pages = generateContinuationLinks(
              route, params, response.data.totalResultSetSize);
          $scope.updateResults(response, tab);
        });
      };

      $scope.updateResults = function(response, tab) {
        tab.loading = false;
        tab.results = response.data.results;
        tab.columns = response.data.columns;  // for PQL Service
        if (!tab.results.length) {
          tab.empty = true;
        }

        // upgrade accordions once they are rendered
        $timeout(componentHandler.upgradeDom);
      };

      $scope.callAPI = function(uri, tab, successCallback) {
        $scope.resetTab(tab);
        tab.loading = true;

        $http.get(uri).then(successCallback, function(response) {
          // on error
          tab.loading = false;
          tab.errormsg = 'HTTP ' + response.status + ' Error';
          if (!networkInfo.code) {
            tab.errormsg += '. Did you forget to select a network?';
          } else {
            tab.errormsg += '. Is your where statement valid?';
          }
        });
      };

      // pagination
      var generateContinuationLinks = function(
          route, params, totalResultSetSize) {
        var pageSize = 25;
        var limit = params.limit;
        var offset = params.offset;

        if (totalResultSetSize === 0) {
          return [];
        } else if (totalResultSetSize) {
          if (totalResultSetSize < limit) {
            limit = totalResultSetSize;
          }
        }

        var continuationLinks = [];
        var totalPages = Math.ceil((limit - offset) / pageSize);
        for (let i = 0; i < totalPages; i++) {
          var uri =
              ('/api/' + route + '?where=' + encodeURIComponent(params.where) +
               '&network_code=' + params.network_code + '&limit=' + limit +
               '&offset=' + offset);
          continuationLinks.push(uri);
          offset += pageSize;
          limit -= pageSize;
        }
        return continuationLinks;
      };

      $scope.navigateToPage = function(tab, newPageNum) {
        if (tab.pageNum === newPageNum || tab.loading) return;
        if (newPageNum >= 1 && newPageNum <= tab.pages.length) {
          tab.pageNum = newPageNum;
          var uri = tab.pages[newPageNum - 1];
          $scope.callAPI(uri, tab, function(response) {
            $scope.updateResults(response, tab);
          });
        }
      };
    });
