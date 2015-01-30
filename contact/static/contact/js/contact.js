var $ = jQuery;

// We need to kick the function off when we finish loading the modal content/
// It appears as in callback to the ajax request that grabs this content in base.html
function initialize_bootstrap_validator_contact() {
    'use strict';
    $('#contact-form').bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        submitButtons: $('#contact-form-submit-button')
    }).on('success.form.bv', function (e) {
        // Prevent form submission
        e.preventDefault();

        // Get the form instance
        var $form = $(e.target);

        // Use Ajax to submit form data
        $.post($form.attr('action'), $form.serialize(), 'json')
            .done(function (response) {
                $('#modal-contact-root').modal('hide');
                $form.data('bootstrapValidator').resetForm(true);
                handle_ajax_response(response);
            })
            .fail(function (response) {
                set_notification($('#contact-notification-root'),
                                   'Uh oh! Something went wrong. Try again in a bit!', 'alert-danger');
            });
    });
}

