request_model_settings = {'REQUEST_STATUSES': (('P', 'Pending'),    # User has not yet accepted or rejected the user
                                               ('C', 'Closed'),     # Event date has passed.
                                                                    # A request must be expired before it can reach this status.
                                               ('E', 'Expired'),    # user does not accept or reject within time limit
                                               ('A', 'Accepted'),   # Ticket sold to this user!
                                               ('D', 'Declined'),   # This user was declined!
                                               ('C', 'Cancelled'),  # The user cancelled their request.
                                               ('T', 'Ticket Cancelled'),  # The user seller cancelled the ticket
                                               ('S', 'Ticket Sold'),       # Other request accepted first
                                               )
                          }

TICKET_REQUESTED_POSTER_SUBJECT = "SpareStub - A User Requested To Buy Your Ticket"
TICKET_REQUESTED_POSTER_TEMPLATE = "asks/ticket_requested_poster_email.html"
TICKET_REQUESTED_REQUESTER_SUBJECT = "SpareStub - Ticket Request Confirmation"
TICKET_REQUESTED_REQUESTER_TEMPLATE = "asks/ticket_requested_requester_email.html"

# What to send a user when his request is marked inactive because of something he did not do
  # 1. Requested ticket expired
  # 2. Requested declined by seller
  # 3. Ticket cancelled by seller
REQUEST_INACTIVE_SUBJECT = "SpareStub - Request Cancelled"
REQUEST_INACTIVE_TEMPLATE = "asks/request_inactive_email.html"

# When a request is accepted by a seller. This email goes to both the buyer and the seller.
REQUEST_ACCEPTED_SUBJECT = "SpareStub - Request Accepted"
REQUEST_ACCEPTED_TEMPLATE = "asks/request_accepted_email.html"
