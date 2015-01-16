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

function initiate_stripe() {

    show_popup_notification_modal('<p>After you close this popup, you will be asked to enter your credit card ' +
        'information. You will not be charged immediately or necessarily at all.</p><p>The seller of this ticket must ' +
        'first approve you and agree to go to the event with you. If he accepts your request, your card will be ' +
        'charged. If he does not accept your request, you will not be charged.</p><p>After initiating this request, you ' +
        'will not be able to request to go to another show on the same day at the same time.</p>', 'warning', true);
}


function prepare_delete_ticket_button() {
    // This looks dumb at first glance. Why do we prepare the modal every time a user clicks on the button?
    // The answer is that this modal is multi-purposed, and another button might use it in the future.
    $('#delete-ticket').on('click', function () {
        can_delete_ticket();
    });
}

function can_delete_ticket() {
    $.post(window.additional_parameters.can_delete_ticket_url, 'json')
        .done(function () {
             show_yes_cancel_modal('<p>Are you sure you want to permanently delete this ticket listing?</p>' +
                                     '<p>Note: Your deleted tickets appear in the Past Tickets section of your profile.</p>',
                                      window.additional_parameters.delete_ticket_url);
        })
        .fail(function (response) {
            var error_message = handle_ajax_response(response.responseJSON);
            show_ajax_message(error_message, 'danger');
        });
}

function can_request_to_buy() {
    /* There are some cases where we will not allow a user to request to buy a ticket.
     * If the ticket was cancelled or the buyer is already going to another show or already requested to buy this ticket
     */

    $.post(window.additional_parameters.can_request_ticket_url,
           {'ticket_id': window.additional_parameters.ticket_id},
           "json")
        .done(function (response) {
            initiate_stripe();
        })
        .fail(function (response) {
            var error_message = handle_ajax_response(response.responseJSON);
            show_ajax_message(error_message, 'danger');
        });

}

function cancel_request_to_buy() {
    $.post(window.additional_parameters.cancel_request_to_buy_url,
           {'ticket_id': window.additional_parameters.ticket_id},
           "json")
        .done(function (response) {
            var message = handle_ajax_response(response);
            show_ajax_message(message, 'success');
            $('#cancel-request').replaceWith('<button id="request-to-buy" class="btn btn-primary">Request To Buy</button>');
            $('#request-to-buy').on('click', request_to_buy);
        })
        .fail(function (response) {
            var error_message = handle_ajax_response(response);
            show_ajax_message(error_message, 'danger');

        });
}

function show_ajax_message(message, type) {
    var ajax_errors = $('#ajax-errors');
    ajax_errors.find('.alert').removeClass('alert-danger').removeClass('alert-success');
    ajax_errors.css('display', '')
               .addClass('alert-' + type)
               .find('p').text(message);
}

function prepare_stripe_button() {
    'use strict';

    $('#request-to-buy').on('click', request_to_buy);

    $(document).on('modal-popup-notification-closed', function () {
        var handler = StripeCheckout.configure({
            key: window.additional_parameters.stripe_public_key,
            image: '/square-image.png',
            token: function (token) {
                  // Use the token to create the charge with a server-side script.
                  // You can access the token ID with `token.id`
                $.post(window.additional_parameters.request_to_buy_url,
                    {'token': token, 'ticket_id': window.additional_parameters.ticket_id},
                     "json")
                    .done(function (response) {
                        var message = handle_ajax_response(response);
                        $('#request-to-buy').replaceWith('<button id="cancel-request" class="btn btn-primary">Cancel Request To Buy</button>')
                        $('#cancel-request').on('click', cancel_request_to_buy);
                        show_ajax_message(message, 'success');
                    })
                    .fail(function () {
                        show_ajax_message('Something went wrong with the payment!', 'danger');
                    });
            }
        });

        // Open Stripe checkout modal
        handler.open({
            name: 'SpareStub',
            description: window.additional_parameters.ticket_title,
            allowRememberMe: true,
            email: window.additional_parameters.user_email,
            panelLabel: '$' + (parseFloat(window.additional_parameters.ticket_amount) + 5).toString() + ' ($' + (parseFloat(window.additional_parameters.ticket_amount)).toString() + ' + $5 fee)'
        });
    });

    // Close Checkout on page navigation
    $(window).on('popstate', function () {
        handler.close();
    });
}

function request_to_buy() {
    // Users cannot request to buy tickets if they are not logged in
    if (!window.additional_parameters.is_authenticated) {
        load_login_modal(true);
        return;
    }
    can_request_to_buy();
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

    $('#cancel-request').on('click', cancel_request_to_buy);
});