/**
 * Created by nicholasdrane on 10/6/14.
 */

var $ = jQuery;
var document = window.document;

function initialize_location_autocomplete() {
    'use strict';
    var locations = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        limit: 5,
        prefetch: {
            url: window.additional_parameters.cities_list_url,
            // the json file contains an array of strings, but the Bloodhound
            // suggestion engine expects JavaScript objects so this converts all of
            // those strings
            filter: function (list) {
                return $.map(list, function (city) {
                    return { name: city[0] + ', ' + city[1],
                             pop: city[2]
                             };
                });
            }
        },
        sorter: function (a, b) {
            var pop_a = a.pop;
            var pop_b = b.pop;
            if (pop_a > pop_b) {
                return -1;
            } else if (pop_a < pop_b) {
                return 1;
            } else {
                return 0;
            }
        }
    });

    // kicks off the loading/processing of `prefetch`
    locations.initialize();

    $('.location-autocomplete').typeahead(
        {
            hint: false
        },
        {
            name: 'locations',
            displayKey: 'name',
            source: locations.ttAdapter()
        }
    );
}

function initialize_date_pickers() {
    var today = new Date();
    var todayDay = today.getDate();
    var todayMonth = today.getMonth() + 1;
    var todayYear = today.getFullYear();
    $('.date-picker').datetimepicker({
        pickTime: false,
        minDate: todayMonth + '/' + todayDay + '/' + todayYear,
        showToday: true
    });
}

$(document).ready(function ($) {
    'use strict';
    $('.contact-form-button').on('click', function () {
        // If the modal content has already been loaded, don't do it again
        if ($('#modal-contact-form-content').children().length > 0) {
            return;
        }
        $.get(window.additional_parameters.contact_form_url, function (data) {
            $('#modal-contact-form-content').html(data);
            initialize_bootstrap_validator_contact();
        });
    });

    $('.signup-form-button').on('click', function () {
        // If the modal content has already been loaded, don't do it again
        if ($('#modal-signup-form-content').children().length > 0) {
            return;
        }
        $.get(window.additional_parameters.signup_form_url, function (data) {
            $('#modal-signup-form-content').html(data);
            initialize_bootstrap_validator_signup();
        });
    });

    $('.login-form-button').on('click', function () {
        // If the modal content has already been loaded, don't do it again
        if ($('#modal-login-form-content').children().length > 0) {
            return;
        }
        $.get(window.additional_parameters.login_form_url, function (data) {
            $('#modal-login-form-content').html(data);
            initialize_bootstrap_validator_login();
        });
    });

    $('.submit-ticket-form-button').on('click', function () {
        // If the modal content has already been loaded, don't do it again
        if ($('#modal-submit-ticket-form-content').children().length > 0) {
            return;
        }
        $.get(window.additional_parameters.submit_ticket_form_url, function (data) {
            $('#modal-submit-ticket-form-content').html(data);
            initialize_bootstrap_validator_submit_ticket();

            // Initialize when the submit-ticket forms loads in addition to when the main page loads.
            // Seeing as the location input box in the ticket submission form won't exists when the page loads,
            // we need to call this initialization function twice.
            initialize_location_autocomplete();
        });
    });

    initialize_date_pickers();
    prepare_ticket_search_dropdown();

    // Initialize when the page loads so that ticker search autocomplete woks
    initialize_location_autocomplete();

    format_ticket_type_select();

}(window.jQuery));