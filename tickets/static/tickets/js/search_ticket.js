/**
 * Created by nicholasdrane on 10/31/14.
 */

var $ = jQuery;

function prepare_ticket_search_dropdown() {
    var is_input_search_clicked = false;
    'use strict';
    // Stop ticket search dropdown from closing when users try to click on any of the dropdown fields.
    $('.dropdown-menu').click(function (e) {
        e.stopPropagation();
    });


    // If the user clicks on the input search box when the dropdown is already open (the hide.bs.dropdown event wouldn't
    // trigger if the dropdown weren't open), do not close the dropdown. We want them to be able to apply filters and
    // then come back to the search input box. This code is terrible, but I wasn't sure how else to check if an event
    // had triggered from another event. The BS event really should tell us the element that was specifically clicked.
    $('#search-ticket-input').click(function (e) {
        is_input_search_clicked = true;
    });

    $('#search-ticket-form').on('hide.bs.dropdown', function (e) {
        if (is_input_search_clicked) {
            // If the dropdown tried to hide, then we either just clicked on the search input field or just clicked
            // off the dropdown box.
            is_input_search_clicked = false;
            return false;
        }
    }).on('shown.bs.dropdown', function (e) {
        is_input_search_clicked = false;
    });
}
/*
function format_ticket_type_select() {
    if
    ticket_types = [];
    $('#search-ticket-type option').each(function () {
        window.additional_parameters.ticket_types.push($(this).attr('value') + '-' + $(this).text());
    });

              <option value="" selected>All Tickets</option>
          {% for option in TICKET_TYPES %}
            <option value="{{ option.0 }}">{{ option.1 }}</option>
}*/