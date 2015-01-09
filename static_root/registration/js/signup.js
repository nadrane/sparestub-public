var $ = jQuery;
var document = window.document;

function validate_user_is_18(birthdate) {
    'use strict';
    /*
    This function will be used by bootstrap validator as a callbackto validate the
    user is 18 years of age.
     */

    // Don't display that the user is not 18 until they've entered an entire date.
    if (birthdate.length === 10) {
        var today = new Date();
        birthdate = new Date(birthdate);
        var age = today.getFullYear() - birthdate.getFullYear();
        var month = today.getMonth() - birthdate.getMonth();
        if (month < 0 || (month === 0 && today.getDate() < birthdate.getDate())) {
            age--;
        }
        return age >= 18;
    }
    return true;
}

// We need to kick the function off when we finish loading the modal content/
// It appears as in callback to the ajax request that grabs this content in base.html
function initialize_bootstrap_validator_signup(redirect) {
    'use strict';
    $('#signup-form').bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        submitButtons: $('#signup-form-submit-button')
        // TODO figure out how we want to handle email validation given that triggers are field specific, not validator specific.
    }).on('success.form.bv', function (e) {
        // Prevent form submission
        e.preventDefault();

        // Get the form instance
        var $form = $(e.target);

        $.post($form.attr('action'), $form.serialize(), 'json')
            .done(function (data, textStatus, xhr) {
                // It's probably redundant to check the json value for true seeing as the server returned a 200 status
                // code, but an extra check never hurts.
                handle_ajax_response(data, $('#signup-notification-root'));
            })
            .fail(function (data, textStatus, xhr) {
                // Obviously there are cases were we never reached the server (internet down or incredibly high loads
                // resulting in the web server turning people away), so we cannot check the JSON object that might or
                // might not have been returned by the application level.
                set_notification($('#signup-notification-root'),
                                 'Uh oh! Something went wrong. Try again in a bit!',
                                 'alert-danger');
                $form.data('bootstrapValidator').resetForm(true);
            });
    });
}