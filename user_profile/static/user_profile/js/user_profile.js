$(document).ready(function ($) {
    'use strict';
    resize_header();  // Do this once when the page initially loads

    // And then every time the page is resized
    $(window).resize(function () {
        resize_header($);
    });

    editable_profile();
}(window.jQuery));

function resize_header() {
    var $header = $('#profile-header');
    var $thumbnail = $('#user-picture > img');
    /* Resize the profile header to be the same size as the thumbnail image */
    $header.css('height', function () {
        var $this = $(this);
        var total_height = parseInt($thumbnail.css('height').replace('px', ''), 10) +
                           parseInt($this.css('padding-top').replace('px', ''), 10) +
                           parseInt($this.css('padding-bottom').replace('px', ''), 10) +
                           parseInt($this.css('margin-top').replace('px', ''), 10) + 10;
        total_height = total_height.toString() + 'px';
        return total_height;
    });
}

function editable_profile() {
    $('#user-picture').hover(function () {
        $('#edit-profile-icon').animate({fontSize: "1.2em"}, 200);
        $('#edit-profile-text').fadeIn(200);
    }, function () {
        $('#edit-profile-icon').animate({fontSize: "1.8em"}, 200);
        $('#edit-profile-text').fadeOut(200);
    });
}