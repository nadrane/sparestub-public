/**
 * Created by nicholasdrane on 11/3/14.
 */

var $ = jQuery;

function initialize_filters() {
    'use strict';
    // Initialize popovers for each of the filter buttons
    $('#filter-payment-method').attr('data-content', function () {
    var html = '<input type="radio" name="Good Faith" value="Good Faith>wtfffffffffsasadasdasd<input type="radio" name="Secure" value="Secure">';

    return html;
    });
    $('#filter-list > li > a').popover();
}

$(document).ready(function ($) {
    'use strict';
    initialize_filters();
}(window.jQuery));


