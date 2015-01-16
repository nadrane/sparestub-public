var document = window.document;
var $ = jQuery;

function accept_request() {
    /* Kick this off when a seller accepts a buyer's request. */
    'use strict';

    var $current_thread = $('.current-thread');
    $.post(window.additional_parameters.accept_request_url,
           {'ticket_id': $current_thread.data('identity-ticket'),
            'other_user_id': $current_thread.data('identity-user')},
            "json")
        .always(function (response) {
            handle_ajax_response(response.responseJSON);
        });
}

function decline_request() {
    /* Kick this off when a seller decline's a buyer's request. */
    'use strict';

    var $current_thread = $('.current-thread');
    $.post(window.additional_parameters.decline_request_url,
           {'ticket_id': $current_thread.data('identity-ticket'),
            'other_user_id': $current_thread.data('identity-user')},
            "json")
        .done(function (response) {
            handle_ajax_response(response.responseJSON);
            toggle_messaging('off');
        })
        .fail(function (response) {
            handle_ajax_response(response.responseJSON);
        });
}


function send_message(e) {
    /* Create a message object when the Send Message button is clicked
    *  Perform checks to make sure the user isn't exchanging contact info or talking about paying outside SpareStub.
    *  Lastly update the conversation body above to include their new message.
    */

    'use strict';
    var $current_thread = $('.current-thread');
    var $new_message_textarea = $('#new-message-textarea');
    var $conversation = $('.conversation');

    var body = $new_message_textarea.val();
    var user_image = $('.talk-bubble').filter('.this-user').find('.talk-bubble-pic').attr('src');

    e.stopPropagation();
    e.preventDefault();

    // Make it appear as if the user's message sent by placing it into the conversation.
    $('#conversation-body').find('.conversation')
                           .append('<div class="talk-bubble this-user">' +
                                     '<img class="talk-bubble-pic pull-left" src="' + user_image + '">' +
                                     '<span class="talk-bubble-contents pull-left">' + body + '</span>' +
                                     '<div class="talk-bubble-timestamp pull-right">Just now' + '</div>' +
                                   '</div>');

    $conversation.animate({'scrollTop': ($conversation[0].scrollHeight)});

    $.post(window.additional_parameters.send_message_url,
           {'other_user_id': $current_thread.data('identity-user'),
            'ticket_id': $current_thread.data('identity-ticket'),
            'body': body
            },
            'json');

    // Blank out the message box so that a new message can be sent
    $new_message_textarea.val('');
}

function set_conversation_body_height() {
    /* We need the height of the body to account for the fixed header above it, while still working on different screen
        sizes.
    */

    // The height of other elements on the page
    var consumed_height = $('#convo-header').outerHeight() +
                          $('#ticket-ribbon').outerHeight() +
                          $('#main-navbar').outerHeight() +
                          $('#new-message-box').outerHeight();

    var new_height = $('html').height() - consumed_height;

    $('#conversation-body').height(new_height);
    $('#current-conversation').find('.conversation').height(new_height);
}

function load_thread ($this, ticket_id, other_user_id) {
    // Find searches descendants but not top level nodes.
    // Filter only searches matched nodes at the top level.
    // We need to first clone to node so that it is not erased from the master list
    $('#convo-header').html($('#all-convo-headers').find('[data-identity-ticket=' + ticket_id + ']')
                                                   .filter('[data-identity-user=' + other_user_id + ']')
                                                   .clone()[0]);

    // Ticket ribbons are not unique based on user, so we do not need a user_id filter
    $('#ticket-ribbon').html($('#all-ticket-ribbons').find('[data-identity-ticket=' + ticket_id + ']')
                                                     .clone()[0]);

    $('#conversation-body').html($('#all-conversation-bodies').find('[data-identity-ticket=' + ticket_id + ']')
                                                              .filter('[data-identity-user=' + other_user_id + ']')
                                                              .clone()[0]);


    // Assign the current thread class to the thread just clicked
    $('.current-thread').removeClass('current-thread');
    $this.addClass('current-thread');

    // Display the most recent messages
    var $conversation = $('.conversation');
    $conversation.scrollTop($conversation[0].scrollHeight);

    // Make sure there aren't remnants from a previous conversation there
    $('#new-message-box').val('');

    // Adjust the message box to account for readonly conversations.
    if (can_message($this)) {
        toggle_messaging('on');
    } else {
        toggle_messaging('off');
    }

    // Need to do these after the thread is loaded since that creates the buttons
    $('.accept-request').on('click', accept_request);
    $('.decline-request').on('click', decline_request);

    mark_messages_read(ticket_id, other_user_id);
}

function mark_messages_read(ticket_id, other_user_id) {
    $.post(window.additional_parameters.mark_messages_read_url,
           {'ticket_id': ticket_id,
            'other_user_id': other_user_id},
           'json');
}

function load_first_thread() {
    var $threads = $('#threads');
    if ($threads.children().length > 0) {
        var ticket_id = $threads.children().data('identity-ticket');
        var other_user_id = $threads.children().data('identity-user');
        load_thread($($threads.children()[0]), ticket_id, other_user_id);
    }
}

function  display_no_tickets_screen() {
    $('#threads').replaceWith('<div id="no-threads" class="col-xs-12">' +
                              '<h3 class="text-center">You have no messages!</h3>' +
                              '<p class="text-center">Find a ticket you like, and shoot the seller a message!</p>' +
                              '</div>');
}

function can_message($thread) {
    /* Can the user message the other user form the inputted thread? */
    return ($thread.data('can-message').toLowerCase() === "true");
}

function toggle_messaging(on_or_off) {
    /* Toggle whether it is possible to message another user. Some conversations are read-only */
    var $new_message_textarea = $('#new-message-textarea');
    if (on_or_off === 'on') {
        $new_message_textarea.removeAttr('disabled')
                             .attr('placeholder', 'Say something...')
                             .attr('rows', 5);

        $('#send-message').css('display', '');
    } else if (on_or_off === 'off') {
        $new_message_textarea.attr('disabled', '')
                             .attr('placeholder', 'This conversation is disabled')
                             .attr('rows', 2);

        $('#send-message').css('display', 'none');


    }
    // Now that the size has changed from the rows attribute, recalcualte the conversation body height
    set_conversation_body_height();
}

// When the user opens the page, load the first thread
$(document).on('ready', function () {
    set_conversation_body_height(); // This should be done first to get the screen looking right as fast as possible.

    var $threads = $('#threads');
    var $thread = $('.thread');

    /* We need to use threads here instead of something else like convo headers. It might seem like we could use any of
     * them, but threads are the only group sorted by last timestamp, we want to display the messages from the thread at
     * the top. The first child of $threads will 100% for sure be the first conversation in the list of the left.
     */
    load_first_thread();

    $('#send-message').on('click', function (e) {
        send_message(e);
    });

    // Load a threads contents when it is clicked
    $thread.on('click', function (e) {
        'use strict';
        var ticket_id = $(this).data('identity-ticket');
        var other_user_id = $(this).data('identity-user');
        load_thread($(this), ticket_id, other_user_id);
    });

    // When a user hovers over a thread, show the delete x button
    $thread.hover(
        function (e) {
            'use strict';
            $(this).find('.delete-conversation').css('display', '');
        },
        function (e) {
            'use strict';
            $(this).find('.delete-conversation').css('display', 'none');
        }
    );

    $('.delete-conversation').on('click', function (e) {

        // Don't allow the .thread.onclick event to fire, causing the thread to display it's contents and the messages to be
        // marked as read.
        e.stopPropagation();

        var $parent = $(this).parent();
        var ticket_id = $parent.data('identity-ticket');
        var other_user_id = $parent.data('identity-user');

        $.post(window.additional_parameters.messages_hidden_toggle_url,
               {'ticket_id': ticket_id,
                'other_user_id': other_user_id},
               'json');

        // Make the conversation gone on the front end;
        $parent.remove();

        if ($('#threads').children().length > 0) {
            load_first_thread();
        } else {
            display_no_tickets_screen();
        }
    });
});

//Make the thread bar stretch down the entire height of the screen, even if there aren't enough
//conversations to fill it.
$(window).on('onload resize', function () {
    'use strict';

    $('html').height(window.innerHeight);
});

$(window).on('resize', function () {
    'use strict';

    set_conversation_body_height();
});