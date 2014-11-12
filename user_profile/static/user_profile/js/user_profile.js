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

function validate_username() {
    /* Make sure that the username does not already exist */

}

function editable_profile() {
    /* Make the profile picture have animations that indicate that it is editable */
    $('#user-picture').hover(function () {
        $('#edit-profile-icon').animate({fontSize: "1.2em"}, 200);
        $('#edit-profile-text').fadeIn(200);
    }, function () {
        $('#edit-profile-icon').animate({fontSize: "1.8em"}, 200);
        $('#edit-profile-text').fadeOut(200);
    });
}

function update_question_form() {
    $('.question-update-form').submit(function (e) {
        e.preventDefault();

        // Get the form instance
        var $form = $(e.target);

        $.post($form.attr('action'), $form.serialize(), 'json')
            .done(function (data, textStatus, xhr) {
                // It's probably redundant to check the json value for true seeing as the server returned a 200 status
                // code, but an extra check never hurts.
                if (data.isSuccessful) {
                    handle_ajax_response(data);
                    set_notification($('#notification-root'), 'Success!',
                                       "You're ready to use SpareStub!", 'alert-success');
                }
            })
            .fail(function (data, textStatus, xhr) {
                // Obviously there are cases were we never reached the server (internet down or incredibly high loads
                // resulting in the web server turning people away), so we cannot check the JSON object that might or
                // might not have been returned by the application level.
                if (has_notification_update(data.responseJSON)) {
                    handle_ajax_response(data.responseJSON, $('#login-notification-root'));
                }
                else {
                    set_notification($('#login-notification-root'), 'Uh oh!',
                                       "Something went wrong. Try again in a bit!", 'alert-danger');
                }
            })
    });
}

function initialize_bootstrap_validator_edit_profile() {
    'use strict';
    $('#edit-profile-form').bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        submitButtons: $('#edit-profile-form-submit-button'),
        excluded: [] // Do not exclude hidden/not displayed fields. This allows us to run an initial round of
                     // validation on the user's current data while the form is closed. Otherwise every field would
                     // just get skipped.
    });
}

$(document).ready(function ($) {
    'use strict';
    update_question_form();

    // Resize the header every time the width of the screen adjusts.
    // CSS will change the profile picture height, so we need to change the header height as well.
    $(window).resize(function () {
        resize_header($);
    });

    // Do not let a user edit a different user's profile
    if (window.additional_parameters.is_owner) {
        editable_profile();
        $('#user-picture').on('click', function () {
            // If the modal content has already been loaded, don't do it again
            if ($('#modal-edit-profile-form-content').children().length > 0) {
                return;
            }

            $.get(window.additional_parameters.edit_profile_form_url, function (data) {
                $('#modal-edit-profile-form-content').html(data);
                initialize_bootstrap_validator_edit_profile();

                // The form comes with the user's current information filled inside it.
                // Validate the form so that all fields do not need to be changed to resumbit the form.
                // As it stands, a field will only be validated if it's changed, and all fields must be validated.
                // We to have to do every field individually because BV actually submits the form to the
                // server using it's validate method, which we obviously don't want.
                var $edit_profile_form = $('#edit-profile-form');
                $edit_profile_form.bootstrapValidator('revalidateField', 'first_name');
                $edit_profile_form.bootstrapValidator('revalidateField', 'last_name');
                $edit_profile_form.bootstrapValidator('revalidateField', 'zip_code');
                $edit_profile_form.bootstrapValidator('revalidateField', 'email');
                $edit_profile_form.bootstrapValidator('revalidateField', 'username');
            });
        });
    }
}(window.jQuery));


$(window).load(function ($) {
    resize_header();  // Do this once when the page initially loads, but we need to make sure the
                      // profile picture has loaded. This is why we use window.load instead of document.ready.
}(window.jQuery));