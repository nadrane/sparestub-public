/**
 * Created by nicholasdrane on 10/10/14.
 */

var set_notification = function (header_message, content_message, message_type) {
   'use strict';
    var $notification_root = $('#notification-root');

    // The close button remove the root and everything inside it when clicked. Instead of using a custom event,
    // Just make sure that the notification root exists before we try to edit it's contents.
    if ($notification_root.length === 0) {
        $('.navbar').after('<div id="notification-root"> \
                              <a href="#" class="close" data-dismiss="alert">×</a> \
                              <strong id="notification-header"></strong> \
                              <span id="notification-content"></span> \
                            </div>');

        // Select the notification-root now that it exists
        $notification_root = $('#notification-root');
    }

    $('#notification-header').text(header_message);
    $('#notification-content').text(content_message);
    $('#notification-root').addClass('alert ' + message_type)
                           .css('display', '');
};

var hide_notification = function () {
    $('notification-root').css('display', 'None');
};