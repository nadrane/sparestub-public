request_model_settings = {'REQUEST_STATUSES': (('P', 'Pending'),    # User has not yet accepted or rejected the user
                                               ('E', 'Expired'),    # Event date has passed, or user does not accept or reject within time limit
                                               ('A', 'Accepted'),   # Ticket sold to this user!
                                               ('D', 'Declined'),   # This user was declined!
                                               ('C', 'Cancelled'),  # The user cancelled their request.
                                               ('T', 'Ticket Cancelled')   # The user seller cancelled the ticket
                                               )
                          }

TICKET_REQUESTED_POSTER_SUBJECT = "SpareStub - A User Requested To Buy Your Ticket"
TICKET_REQUESTED_POSTER_TEMPLATE = "asks/ticket_requested_poster_email.html"
TICKET_REQUESTED_REQUESTER_SUBJECT = "SpareStub - Ticket Request Confirmation"
TICKET_REQUESTED_REQUESTER_TEMPLATE = "asks/ticket_requested_bidder_email.html"

# What to send the user when the request is cancelled becuase it's associated ticket was deactivated
TICKET_CANCELLED_SUBJECT = "SpareStub - Request Cancelled"
TICKET_CANCELLED_TEMPLATE = "asks/ticket_requested_bidder_email.html"
