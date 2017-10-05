(function () {
    angular
        .module('djangochannels', [
            'djangochannels.services',
            'djangochannels.controllers',
            'djangochannels.directives'
        ]);

    angular
        .module('djangochannels.config', []);

    angular
        .module('djangochannels.services', []);

    angular
        .module('djangochannels.controllers', []);

    angular
        .module('djangochannels.directives', []);

    angular
        .module('djangochannels')
        .run(run);

    run.$inject = [];

    function run () {
        console.log('Angular app started.');
    }

    angular
        .module('djangochannels.services')
        .service('WebSocketService', WebSocketService);

    WebSocketService.$inject = ['$window'];

    function WebSocketService ($window) {
        var self = this;

        var defaultOptions = {
            debug: true, reconnectInterval: 3000
        };

        var _init = function (options) {
            var ws_scheme = $window.location.protocol === "https:" ? "wss" : "ws";
            var ws_path = ws_scheme + '://' + $window.location.host + $window.location.pathname + "stream/";

            if (options) {
                for (var key in defaultOptions) {
                    if (!(key in options)) {
                        options[key] = defaultOptions[key];
                    }
                }
            }

            return new ReconnectingWebSocket(ws_path, options);
        };

        var wsInstance = undefined;

        this.createWebSocket = function (options) {
            if (!wsInstance) {
                wsInstance = _init(options);
            }

            return wsInstance;
        };

        this.start = function (options) {
            return self.createWebSocket(options);
        };
    }

    angular
        .module('djangochannels.services')
        .service('MessagesService', MessagesService);

    MessagesService.$inject = ['$http', '$window'];

    function MessagesService($http, $window) {
        this.all = function (params) {
            // console.log($window.location.pathname);
            return $http({
                url: '/api' + $window.location.pathname,
                method: 'GET',
                params: params
            });
        }
    }

    angular
        .module('djangochannels.controllers')
        .controller('MainController', MainController);

    MainController.$inject = [];

    function MainController() {
        var vm = this;

        function activate () {}
        activate();
    }

    angular
        .module('djangochannels.controllers')
        .component('messageComponent', {
            controller: MessageController,
            controllerAs: 'vm',
            bindings: {},
            template: [
                '<div class="well">',
                    '<div class="" ng-repeat="message in vm.messages">',
                        '<message-detail message="message"',
                            'message-index="$index"',
                            'on-update="vm.doUpdate(message, messageIndex)"',
                            'on-delete="vm.doDelete(message, messageIndex)"></message-detail>',
                    '</div>',
                '</div>',
                '<message-form on-create="vm.doCreate(message)"></message-form>'
            ].join('')
        });

    angular
        .module('djangochannels.controllers')
        .controller('MessageController', MessageController);

    MessageController.$inject = ['$scope', 'MessagesService', 'WebSocketService', '$timeout'];

    function MessageController($scope, MessagesService, WebSocketService, $timeout) {
        var vm = this;

        vm.params = {};

        vm.messages = [];

        function getMessages () {
            MessagesService.all(vm.params)
                .then(function (response) {
                    console.log(response.data);
                    vm.messages = vm.messages.concat(response.data.results);
                    console.log(vm.messages);
                })
                .catch(function (error) {
                    console.log(error);
                });
        }

        function activate () {
            vm.websocket = WebSocketService.start();

            vm.websocket.onopen = function () {
                console.log("Connected to notification socket");
            };

            vm.websocket.onclose = function () {
                console.log("Disconnected to notification socket");
            };

            getMessages();
        }

        vm.doCreate = function (message) {
            $timeout(function () {
                vm.messages.push(message);
            });
        };

        vm.doUpdate = function (message, messageIndex) {
            vm.messages[messageIndex] = message;
        };

        vm.doDelete = function (message, messageIndex) {
            vm.messages.splice(messageIndex, 1);
        };

        vm.$onInit = function () {
            // console.log('oninit');
            activate();
        };

        vm.$onChanges = function (changesObj) {
            // console.log('onchange');
        };

        vm.$onDestroy = function () {
            // console.log('ondestroy');
        };

        vm.$doCheck = function () {
            // console.log('docheck');
        };

    }

    angular
        .module('djangochannels.controllers')
        .component('messageForm', {
            controller: MessageFormController,
            controllerAs: 'vm',
             // Binds the attributes to the component controller.
            bindings: {
                onCreate: '&'
            },
            template: [
                '<div class="message-form">',
                    '<form ng-submit="vm.submit()" class="container">',
                        '<div class="row">',
                            '<div class="col-xs-12">',
                                '<div class="form-group label-floating">',
                                    '<div class="input-group">',
                                        '<span class="input-group-addon">',
                                            '<i class="material-icons" style="color: white;">chat</i>',
                                        '</span>',
                                        '<input type="text" id="content" class="form-control" style="color: white;" ng-model="vm.message.content">',
                                        '<p class="help-block">The label is inside the <code>input-group</code> so that it is positioned properly as a placeholder.</p>',
                                        '<span class="input-group-btn">',
                                            '<button type="submit" class="btn btn-primary btn-fab" ng-disabled="vm.isSubmitted">',
                                                '<i class="material-icons" style="color: white;">send</i>',
                                            '</button>',
                                        '</span>',
                                    '</div>',
                                '</div>',
                                '<br>',
                            '</div>',
                        '</div>',
                    '</form>',
                '</div>'
            ].join('')
        });

    angular
        .module('djangochannels.controllers')
        .controller('MessageFormController', MessageFormController);

    MessageFormController.$inject = ['$scope', 'WebSocketService'];

    function MessageFormController($scope, WebSocketService) {
        var vm = this;

        vm.message = {};

        vm.isSubmitted = false;

        vm.submit = function () {
            // return if message is empty
            if (vm.message.content) {
                if (!vm.message.content.trim()) {
                    return;
                }
            } else {
                return;
            }

            vm.isSubmitted = true;
            // Stringify the json
            var message = JSON.stringify(vm.message);
            vm.websocket.send(message);

            vm.message = {};
            vm.isSubmitted = false;
        };

        function activate () {
            vm.websocket = WebSocketService.start();

            vm.websocket.onmessage = function (message) {
                // Parse the JSON
                var data = JSON.parse(message.data);
                console.log("Got message ", data);
                vm.onCreate({message: data});
            };

            vm.websocket.onopen = function () {
                console.log("Connected to notification socket");
            };

            vm.websocket.onclose = function () {
                console.log("Disconnected to notification socket");
            };
        }

        vm.$onInit = function () {
            // console.log('oninit');
            activate();
        };

        vm.$onChanges = function (changesObj) {
            // console.log('onchange');
            console.log(changesObj);
        };

        vm.$onDestroy = function () {
            // console.log('ondestroy');
        };

        vm.$doCheck = function () {
            // console.log('docheck');
        };

    }

    angular
        .module('djangochannels.controllers')
        .component('messageDetail', {
            controller: MessageDetailController,
            controllerAs: 'vm',
            bindings: {
                message: '<',
                onDelete: '&',
                onUpdate: '&'
            },
            template: [
                '<div class="" style="padding: 10px 0; border-bottom: 1px solid teal;">',
                    '<div class="">',
                        '<div class="my-user-item">',
                            '<a class="my-user-username" ui-sref="profile({ username: vm.message.user.username })"',
                                'ng-click="$event.stopPropagation()">',
                                    '<img class="my-user-avatar" src="http://i.stack.imgur.com/Dj7eP.jpg">',
                                        '<span style="padding-left: 10px;">{{vm.message.user.username}}</span></a>',

                            '<div class="my-user-date">',
                                '<span>{{ vm.message.updated_at | date: "d, MMM, yyyy \'at\' h:mma" }}</span>',
                            '</div>',

                            '<div class="my-user-options dropdown"',
                                 'ng-if="vm.user.username === vm.message.user.username">',
                                            '<span class="dropdown-toggle" data-toggle="dropdown">',
                                                '<i class="material-icons teal">more_vert</i>',
                                            '</span>',
                                '<ul class="dropdown-menu dropdown-menu-right">',
                                    '<li><a href="javascript:void(0)" class="no-margin btn btn-primary" ng-click="vm.doEdit($index)"><h5>Edit</h5></a></li>',
                                    '<li><a href="javascript:void(0)" class="no-margin btn btn-danger" ng-click="vm.doDelete($index)">',
                                        '<h5>Delete</h5>',
                                    '</a></li>',
                                '</ul>',
                            '</div>',
                        '</div>',
                    '</div>',

                    '<div class="" style="padding: 0 50px;">',
                        '<h4 class="text-adjust" ng-if="!vm.message.editMode" ng-bind="vm.message.content"></h4>',

                        '<form ng-submit="vm.submit()" ng-if="vm.message.editMode">',
                            '<div class="form-group no-margin" ng-class="{\',has-error\': vm.message.errors.content}">',
                                '<label class="control-label">Content</label>',
                                '<textarea class="form-control"',
                                          'name="content"',
                                          'rows="2"',
                                          'required',
                                          'auto-grow-dir',
                                          'agd-message="vm.message.content"',
                                          'ng-model="vm.message.content"></textarea>',
                            '</div>',
                            '<span class="help" ng-if="vm.message.errors.content"',
                                  'ng-bind="vm.message.errors.content"></span>',
                            '<div class="form-group no-margin">',
                                '<div class="text-right">',
                                    '<button type="button" class="btn btn-warning"',
                                            'ng-click="vm.message.editMode = !vm.message.editMode">Cancel</button>',
                                    '<button type="submit" class="btn btn-raised btn-primary"',
                                        'ng-disabled="vm.isSubmitted">Submit</button>',
                                '</div>',
                            '</div>',
                        '</form>',
                    '</div>'
            ].join('')
        });

    angular
        .module('djangochannels.controllers')
        .controller('MessageDetailController', MessageDetailController);

    MessageDetailController.$inject = ['MessagesService'];

    function MessageDetailController (MessagesService) {
        var vm = this;

        function activate () {
            // console.log('MDController loaded');
        }

        vm.delete = function () {
            vm.onDelete(message);
        };

        vm.update = function () {
            vm.onUpdate({message: vm.message});
        };

        vm.$onInit = function () {
            // console.log('oninit');
            activate();
        };

        vm.$onChanges = function (changesObj) {
            // console.log('onchange');
        };

        vm.$onDestroy = function () {
            // console.log('ondestroy');
        };

        vm.$doCheck = function () {
            // console.log('docheck');
        };

    }

})();
