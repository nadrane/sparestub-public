from .models import ForgotPasswordLink


# Turn this into a task and make sure it does a bulk, single transaction set
# Run this ever 24 hours. There's no need to keep a datetime on the forgot password links
def expire_forgot_password_links():
    links = ForgotPasswordLink.objects.filter(expired=False)
    if links:
        links.expired = True
        links.save()
    return