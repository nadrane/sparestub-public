/**
 * Created by Nick on 4/13/14.
 */

$(document).ready(function ($, window) {
    'use strict';
    $('#logout-button').click(function () {
        if (window.sessionStorage.fb_authentication_status === 'connected') {
            FB.logout(function (response) {
                window.sessionStorage.fb_uid = '';
                window.sessionStorage.fb_access_token = '';
                window.sessionStorage.fb_authentication_status = 'not_authorized';
            });
        }
    });
}(jQuery, window));

/*
Do we really need AJAX here... probably not.

$(document).ready(function ($) {
    $('#logout-button').click(function () {
        $('navigation_bar_right').replaceWith(navbar_right_base);  // navbar_right_bar is cached in signup.js

        $.ajax({
            type: 'GET',
            url: '/share/more_listings',  // This is not entirely right since we really should return the first set of
                                          // listings, not the second. But it's okay. If we randomize more_listings
                                          // (probably will), it will work out great.
            dataType: 'json',
            success: function (json_response) {
                // $container is defined in listing_page.js when we setup masonry
                var $container = $('#listing-container'),
                    $new_thumbnails = $(json_response).filter('.thumbnail-wrapper');

                $container.append($new_thumbnails);

                $container.imagesLoaded(function () {
                    $new_thumbnails.show(); // Listings come from the server with display: none set.
                                            // Avoid temporarily displaying listings that are incorrectly formatted before
                                            // Masonry kicks in.
                    $container.masonry('appended', $new_thumbnails);  // Update the Masonry container
                });
            }
        });
    });
}(jQuery));

    */