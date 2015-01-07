//Make the thread bar stretch down the entire height of the screen, even if there aren't enough
//conversations to fill it.
$(window).on('onload resize', function () {
    $('html').height(window.innerHeight);
});

function load_thread (ticket_id, other_user_id) {
    // Find searches descendants but not top level nodes.
    // Filter only searches matched nodes at the top level.
    // We need to first clone to node so that it is not erased from the master list
    $('#convo-header').html($('#all-convo-headers').find('[data-identity-ticket=' + ticket_id + ']')
                                                   .filter('[data-identity-user=' + other_user_id + ']')
                                                   .clone()[0]);

    $('#ticket-ribbon').html($('#all-ticket-ribbons').find('[data-identity-ticket=' + ticket_id + ']')
                                                     .filter('[data-identity-user=' + other_user_id + ']')
                                                     .clone()[0]);

    $('#conversation-body').html($('#all-conversation-bodies').find('[data-identity-ticket=' + ticket_id + ']')
                                                              .filter('[data-identity-user=' + other_user_id + ']')
                                                              .clone()[0]);

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
        load_thread(ticket_id, other_user_id);
    }
});

// Load a threads contents when it is clicked
$('.thread').on('click', function (e) {
    'use strict';
    var ticket_id = $(this).data('identity-ticket');
    var other_user_id = $(this).data('identity-user');
    load_thread(ticket_id, other_user_id);
});
