from .models import Customer
from utils.networking import ajax_http


def customer_exists(request):
    """
    Return whether a Stripe customer record exists for the requesting user
    """

    if request.user.is_anonymous():
        return ajax_http(False, 400)
    elif Customer.get_customer_from_user(request.user):
        return ajax_http(True, 200)
    else:
        return ajax_http(False, 400)