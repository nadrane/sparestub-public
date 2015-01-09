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
        $('#message-user-form-submit-button').on('click', function () {
            modal_message_user_button();
        });

    });
}

function prepare_delete_ticket_button() {
    // This looks dumb at first glance. Why do we prepare the modal every time a user clicks on the button?
    // The answer is that this modal is multi-purposed, and another button might use it in the future.
    $('#delete-ticket').on('click', function () {
        prepare_yes_cancel_modal('Are you sure you want to permanently delete this ticket listing?', window.additional_parameters.delete_ticket_url);
    });
}

//TODO this is somewhat of a hack to override what the stripe button reads
function prepare_stripe_button() {
    if (!window.additional_parameters.is_confirmed) {
        set_notification('You need to confirm your email address before you can request to buy a ticket. <a id="resend-confirm-email" href="{% url "create_email_confirmation_link" %}">Resend verification email</a>');
    }

    var handler = StripeCheckout.configure({
        key: window.additional_parameters.stripe_public_key,
        image: '/square-image.png',
        token: function(token) {
          // Use the token to create the charge with a server-side script.
          // You can access the token ID with `token.id`
        }
    });

    $('#customButton').on('click', function(e) {
      // Open Checkout with further options
      handler.open({
        name: 'Demo Site',
        description: '2 widgets ($20.00)',
        amount: 2000
      });
      e.preventDefault();
    });

    // Close Checkout on page navigation
    $(window).on('popstate', function() {
      handler.close();
    });

}

function modal_message_user_button() {
    /* When the user clicks the Send Message button inside the modal messaging form, this tag is called to contact the
     * server and add the message to the database.
     */
    $.post(window.additional_parameters.send_message_url,
           {'other_user_id': window.additional_parameters.user_id,
            'ticket_id': window.additional_parameters.ticket_id,
            'body': $('#message-user-body').val()
            },
            'json');
}

$(document).ready(function ($) {
    $('.message-user').on('click', function () {
        load_message_user_modal(true);
    });  // The show_modal parameter is false because we can expect the data attributes
                                        // in the HTML to handle it for us

    prepare_delete_ticket_button();
    prepare_stripe_button();
});