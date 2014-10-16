var $ = jQuery;
var document = window.document;

// We need to kick the function off when we finish loading the modal content/
// It appears as in callback to the ajax request that grabs this content in base.html
function initialize_bootstrap_validator_login() {
    'use strict';
    $('#login-form').bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        submitButtons: $('#login-form-submit-button')
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
                    $('#modal-login-root').modal('hide');
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
            .always(function () {
                $form.data('bootstrapValidator').resetForm(true);
            });
    });
}