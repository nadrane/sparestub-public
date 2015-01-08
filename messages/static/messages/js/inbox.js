//Make the thread bar stretch down the entire height of the screen, even if there aren't enough
//conversations to fill it.
$(window).on('onload resize', function () {
    $('html').height(window.innerHeight);
});

$(window).on('resize', function () {
    set_conversation_body_height();
});

$(document).on('ready', function () {
    set_conversation_body_height();
});

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
                           .append('<div class="talk-bubble-wrapper">' +
                                   '<div class="talk-bubble pull-left this-user">' +
                                   '<img class="talk-bubble-pic pull-left" src="' + user_image + '">' +
                                   '<div class="talk-bubble-contents pull-left">' + body +
                                   '</div>' +
                                   '</div>' +
                                   '<div class="talk-bubble-timestamp pull-right">Just now' +
                                   '</div>' +
                                   '</div>');

    $conversation.animate({'scrollTop': ($conversation[0].scrollHeight)});

    $.post(window.additional_parameters.send_message_url,
           {'receiver_id': $current_thread.data('identity-user'),
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

    mark_messages_read(ticket_id, other_user_id);
}

function mark_messages_read(ticket_id, other_user_id) {
    $.post(window.additional_parameters.mark_messages_read_url,
           {'ticket_id': ticket_id,
            'other_user_id': other_user_id},
           'json');
}

// When the user opens the page, load the first thread
$(document).on('ready', function () {
    var $all_convo_headers = $('#all-convo-headers');
    if ($all_convo_headers.children().length > 0) {
        var ticket_id = $all_convo_headers.children().data('identity-ticket');
        var other_user_id = $all_convo_headers.children().data('identity-user');
        load_thread($($('#threads').children()[0]), ticket_id, other_user_id);
    }

    $('#send-message').on('click', function (e) {
        send_message(e);
    });
});

// Load a threads contents when it is clicked
$('.thread').on('click', function (e) {
    'use strict';
    var ticket_id = $(this).data('identity-ticket');
    var other_user_id = $(this).data('identity-user');
    load_thread($(this), ticket_id, other_user_id);
});
