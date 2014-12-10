// We need to kick the function off when we finish loading the modal content/
// It appears as in callback to the ajax request that grabs this content in base.html
function initialize_bootstrap_validator_message_user() {
    'use strict';

    $('#message-user-form').bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        submitButtons: $('#message-user-form-submit-button')
    }).on('success.form.bv', function (e) {
        // Prevent form submission
        e.preventDefault();

        // Get the form instance
        var $form = $(e.target);

        $.post($form.attr('action'), $form.serialize(), 'json');
    });
}

function load_message_user_modal(show_modal) {
    'use strict';
    /* Load the message user modal content from the server and display that form if requested.
    params: show_modal - true = Display modal message user form immediately.
                         false = Do not display the modal sign up form.
    */

    if (!window.additional_parameters.is_authenticated) {
        load_login_modal(true);
        return;
    }

    var $modal_message_user_form_content = $('#modal-message-user-form-content');
    // If the modal content has already been loaded, don't do it again
    if ($modal_message_user_form_content.children().length > 0) {
        if (show_modal) {
            $('#modal-message-user-root').modal('show');
        }
        return;
    }
    $.get(window.additional_parameters.message_user_form_url, function (data) {
        $modal_message_user_form_content.html(data);
        initialize_bootstrap_validator_message_user();
        if (show_modal) {
            $('#modal-message-user-root').modal('show');
        }
    });
}

function prepare_delete_ticket_button() {
    // This looks dumb at first glance. Why do we prepare the modal every time a user clicks on the button?
    // The answer is that this modal is multi-purposed, and another button might use it in the future.
    $('#delete-ticket').on('click', function () {
        prepare_yes_cancel_modal('Are you sure you want to permanently delete this ticket listing?', window.additional_parameters.delete_ticket_url);
    });
}

$(document).ready(function ($) {
    $('.message-user').on('click', function () {
        load_message_user_modal(true);
    });  // The show_modal parameter is false because we can expect the data attributes
                                        // in the HTML to handle it for us
    prepare_delete_ticket_button();
});