request_model_settings = {'REQUEST_STATUSES': (('P', 'Pending'),    # User has not yet accepted or rejected the user
                                               ('C', 'Closed'),     # Event date has passed.
                                                                    # A request must be expired before it can reach this status.
                                               ('E', 'Expired'),    # user does not accept or reject within time limit
                                               ('A', 'Accepted'),   # Ticket sold to this user!
                                               ('D', 'Declined'),   # This user was declined!
                                               ('C', 'Cancelled'),  # The user cancelled their request.
                                               ('T', 'Ticket Cancelled'),  # The user seller cancelled the ticket
                                               ('S', 'Ticket Sold'),       # Other request accepted first
                                               ('I', 'Inactive Ticket')    # The user's account was deactivated, and
                                                                           # so were the associated requests
                                               )
                          }

# When a request is submitted, these go to the poster of the ticket
REQUEST_RECEIVED_SUBJECT = "SpareStub - A User Requested To Buy Your Ticket"
REQUEST_RECEIVED_TEMPLATE = "asks/request_received.html"

# When a request is submitted, these go to the submitter of the request
REQUEST_SENT_SUBJECT = "SpareStub - Ticket Request Confirmation"
REQUEST_SENT_TEMPLATE = "asks/request_sent.html"

# What to send a user when his request is marked inactive because
  # 1. Requested ticket expired
  # 2. Requested declined by seller
  # 3. Ticket cancelled by seller
REQUEST_INACTIVE_SUBJECT = "SpareStub - Request Not Accepted"
REQUEST_INACTIVE_TEMPLATE = "asks/request_inactive.html"

# What to send a seller when a user who requested to buy his ticket cancelled it
REQUEST_CANCELLED_TO_SELLER_SUBJECT = "SpareStub - Request Cancelled"
REQUEST_CANCELLED_TO_SELLER_TEMPLATE = "asks/request_cancelled_to_seller.html"

# When a request is accepted by a seller. This email goes to both the buyer and the seller.
REQUEST_ACCEPTED_SUBJECT = "SpareStub - Request Accepted"
REQUEST_ACCEPTED_TEMPLATE = "asks/request_accepted.html"
