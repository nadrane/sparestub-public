// We need to kick the function off when we finish loading the modal content/
// It appears as in callback to the ajax request that grabs this content in base.html
function initialize_bootstrap_validator() {
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

        // Get the BootstrapValidator instance
        var bv = $form.data('bootstrapValidator');

        //  TODO figure out if we need to handle AJAX failure. What does this mean? Does it never reach the server?
        //    or did the server return a bad status code? Does the browser give a status code of it's own if it can't
        //    reach the server? clearly the server sends 4xx of some sort if it's too busy.
        // Use Ajax to submit form data
        $.post($form.attr('action'), $form.serialize(), function (result) {
            bv.resetForm(true);
            $('#modal-contact-root').modal('hide');
            set_notification('Success!', 'Your email has been sent successfully!', 'alert-success');
        }, 'json');
    });
}

