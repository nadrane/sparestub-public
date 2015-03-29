$(document).on('ready', function () {
    $('#learn-more').on('click', function () {
        $('html, body').animate({'scrollTop': $('#introduction').height() + $('.navbar').height()}, 1000); //body is used by webkit, html is used by firefox
    });

    $('#search-now').on('click', function (e) {
        e.stopPropagation(); // If the event propagates up, it will actually close the dropdown right after it opens.

        // Check to see if the navigation bar is compressed, and if it is, we need to uncollapase it before
        // showing the search-ticket dropdown.
        if ($(window).width() < 768) {
            $('#navbar-collapse').collapse('show'); // Make sure that the search bar is visible currently.
        }
        $('#search-ticket-input').dropdown('toggle');
    });
});

$(document).ready(function () {
    // avoiding iphone / ipad / ipod for now.
    if (navigator.userAgent.search(/Iphone/i) >= 0)
        return;

    if (navigator.userAgent.search(/Ipod/i) >= 0)
        return;

    if (navigator.userAgent.search(/Ipad/i) >= 0)
        return;

    var constant_height = $('.navbar').outerHeight(true) +
                          parseInt($('#introduction').css('padding-top'), 10) +
                          $('#top-intro1').outerHeight(true) +
                          $('#top-intro2').outerHeight(true) +
                          $('#intro-button-div').outerHeight(true) +
                          $('#learn-more').outerHeight(true);

    // normal
    var new_padding = $(window).height() - constant_height;

    // override (chrome)
    if (navigator.userAgent.search("Chrome") >= 0)
        new_padding = ($(window).height() * .30) - constant_height; // fixing some fucked up chrome bug!

    //$('#debugging').html(navigator.userAgent);

    if (new_padding < 10) {
        new_padding = 10;
    }
    $('#buffer').height(new_padding);
});

(function () {
    'use strict';
    var ios = /(iPad|iPhone|iPod)/g.test(navigator.userAgent);
    // IOS devices do not properly support fixed background images. Change them to scroll if the device is ios.
    if (ios) {
        document.getElementById('introducing-sparestub').style.backgroundAttachment = 'scroll';
    }
}());