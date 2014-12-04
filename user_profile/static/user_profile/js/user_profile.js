function resize_header() {
    var $header = $('#profile-header');
    var $thumbnail = $('#user-picture img');
    /* Resize the profile header to be the same size as the thumbnail image */
    $header.css('height', function () {
        var $this = $(this);
        var total_height = parseInt($thumbnail.css('height').replace('px', ''), 10) +
                           parseInt($this.css('padding-top').replace('px', ''), 10) +
                           parseInt($this.css('padding-bottom').replace('px', ''), 10) +
                           parseInt($this.css('margin-top').replace('px', ''), 10) + 10;
        return total_height;
    });
}

$(document).ready(function ($) {
    'use strict';
    // Resize the header every time the width of the screen adjusts.
    // CSS will change the profile picture height, so we need to change the header height as well.
    $(window).resize(function () {
        resize_header($);
    });
}(window.jQuery));


$(window).load(function ($) {
    resize_header();  // Do this once when the page initially loads, but we need to make sure the
                      // profile picture has loaded. This is why we use window.load instead of document.ready.
}(window.jQuery));