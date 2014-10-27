var $ = jQuery;
var document = window.document;

function validate_date_not_before_today(value, validator, $field) {
    'use strict';
    /*
    This function will be used by bootstrap validator as a callbackto validate the
    event date of the ticket to ensure that it is not before the current date.
     */

    var value_array = value.split('/');
    var inputted_date = new Date(value_array[2], value_array[0] - 1, value_array[1]);
    var today = new Date();
    inputted_date.setHours(0);
    inputted_date.setMinutes(0);
    inputted_date.setSeconds(0);
    inputted_date.setMilliseconds(0);
    today.setHours(0);
    today.setMinutes(0);
    today.setSeconds(0);
    today.setMilliseconds(0);
    if (inputted_date >= today) {
        return true;
    }
    return false;
}

function prepend_price_with_currency() {
    return//TODO need to figure something out here for the price
}

function validate_time_not_before_now(value, validator, $field) {
    'use strict';
    /*
    This function will be used by bootstrap validator as a callbackto validate the
    event time of the ticket to ensure that it is not before now.
     */

    // If there is a space before AM/PM, remove it
    var inputted_time = value.replace(' ', '');

    inputted_time = inputted_time.toLowerCase();

    var is_morning = inputted_time.find('am');
    var is_evening = inputted_time.find('pm')



    if (is_morning !== -1) {
        // Now that we know if morning or evening was entered, remove that part of the string
        inputted_time = inputted_time.repalce('am', '');

        var inputted_hour = inputted_time.split(':')[0];
        var inputted_minute = inputted_time.split(':')[1];
    }
    // Better be true
    else if (is_evening !== -1) {
        // Now that we know if morning or evening was entered, remove that part of the string
        inputted_time = inputted_time.repalce('pm', '');

        var inputted_hour = inputted_time.split(':')[0] + 12;
        var inputted_minute = inputted_time.split(':')[1];
    }
    var today = new Date();
    var today_hours = today.getHours();
    var today_minutes = today.getMinutes();

    if (inputted_hour > today_hours) {
        return true
    }

    else if (inputted_hour < today_hours) {
        return false;
    }
}

// We need to kick the function off when we finish loading the modal content/
// It appears as in callback to the ajax request that grabs this content in base.html
function initialize_bootstrap_validator_submit_ticket() {
    'use strict';
    var today = new Date();
    var todayDay = today.getDate();
    var todayMonth = today.getMonth() + 1;
    var todayYear = today.getFullYear();
    $('#submit-ticket-date-picker').datetimepicker({
        pickTime: false,
        minDate: todayMonth + '/' + todayDay + '/' + todayYear,
        showToday: true
    });

    $('#submit-ticket-time-picker').datetimepicker({
        pickDate: false
    });


    // Configure the ticket price to work as a currency
    $('#submit-ticket-price').autoNumeric('init')
        // autoNumeric completely breaks bootstrap validator. Just make sure the field is validated when we lose focus.
                             .blur(function () { $('#submit-ticket-form').bootstrapValidator('revalidateField', 'price'); });




    $('#submit-ticket-form').bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        submitButtons: $('#submit-ticket-form-submit-button')
    }).on('success.form.bv', function (e) {
        // Prevent form submission
        e.preventDefault();

        // Get the form instance
        var $form = $(e.target);

        $.post($form.attr('action'), $form.serialize(), 'json')
            .done(function (data, textStatus, xhr) {
                // It's probably redundant to check the json value for true seeing as the server returned a 200 status
                // code, but an extra check never hurts.
                if (data.isSuccessful) {
                    handle_ajax_response(data);
                    $('#modal-submit-ticket-root').modal('hide');
                    set_notification($('#notification-root'), 'Success!',
                                       "You're ticket will become visible to other users shortly", 'alert-success');
                }
            })
            .fail(function (data, textStatus, xhr) {
                // Obviously there are cases were we never reached the server (internet down or incredibly high loads
                // resulting in the web server turning people away), so we cannot check the JSON object that might or
                // might not have been returned by the application level.
                if (has_notification_update(data.responseJSON)) {
                    handle_ajax_response(data.responseJSON, $('#submit-ticket-notification-root'));
                } else {
                    set_notification($('#submit-ticket-notification-root'), 'Uh oh!',
                                       "Something went wrong. Try again in a bit!", 'alert-danger');
                }
            })
            .always(function () {
                $form.data('bootstrapValidator').resetForm(true);
            });
    });

    // Bootstrap validator will break the datetime picker. We need this function to undo the breakage.
    $('#submit-ticket-date-picker').on('dp.change dp.show', function (e) {
        $('#submit-ticket-form').bootstrapValidator('revalidateField', 'start_date');
    });

    // Bootstrap validator will break the datetime picker. We need this function to undo the breakage.
    $('#submit-ticket-time-picker').on('dp.change dp.show', function (e) {
        $('#submit-ticket-form').bootstrapValidator('revalidateField', 'start_time');
    });

    //Listen for typeahead event where the user selects a location. We need to store the associated zipcode to send it
    // back to the server when this events triggers, otherwise we won't be able to access the location object
    // (and thus the zipcode) again.
    $('#submit-ticket-form').bind('typeahead:selected', function (e, suggestion, dataset) {
        $('#submit-ticket-zipcode').attr('value', suggestion.zip_code);
    });
}

function initialize_typeahead_submit_ticket() {
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
                             pop: city[2],
                             zip_code: city[3]
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

    $('#submit-ticket-location').typeahead(
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