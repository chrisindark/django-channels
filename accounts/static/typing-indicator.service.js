(function () {
    angular
        .module('djangochannels.services')
        .service('TypingIndicator', TypingIndicator);

    TypingIndicator.$inject = ['$rootScope'];

    function TypingIndicator ($rootScope) {
        var self = this;

        this.usersTyping = [];
        this.channel = '';

        // Typing indicator of the current user
        this.isCurrentUserTyping = false ;

        var init = function () {
            console.log('');
        };

        var updateTypingUserList = function (event) {
            // We don't want to receive our own presence events
            if (event['uuid'] === currentUser) return;

            // Add people typing
            if (event['action'] === 'state-change' && event['data']['isTyping']){

            // Check if not already in the array
            if (!_.find(self.usersTyping, { uuid: event['uuid']}))
                self.usersTyping.push({uuid: event['uuid']});
            } else if ( ( event['action'] === 'state-change' &&
                    event['data']['isTyping'] === false ) || event['action'] === 'timeout' ||
                    event['action'] === 'leave' ) {
                _.remove(self.usersTyping, function (user) {
                    return user['uuid'] === event['uuid'];
                });
            }

            $rootScope.$digest();
        };

        var setTypingState = _.debounce(function (isTyping) {
            self.isCurrentUserTyping = isTyping;
            // Pubnub.state({
            //   channel: self.channel,
            //   uuid: currentUser,
            //   state: { isTyping: self.isCurrentUserTyping }
            // });

        },400);

        var getUsersTyping = function (uuid) {
            return self.usersTyping;
        };

        var startTyping = function () {
            setTypingState(true)
        };


        var stopTyping = function(){
            setTypingState(false)
        };

        var isCurrentUserTyping = function () {
            return self.isCurrentUserTyping;
        };

        init();

    }

    angular
        .module('app')
        .directive('typeTracking', typeTracking);

    typeTracking.$inject = ['TypingIndicatorService'];

    function typeTracking (TypingIndicatorService) {
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                scope.$watch(attrs['ngModel'], function (newValue) {
                    // We are notified each time the value of the input change
                    console.log('typingValue', newValue)
                });
            }
        };
    }

})();
