__author__ = 'Nick'

RESTRICTED_URLS = []

# We create a custom url for each user's profile.html. It might be based on email (possibly name, though).
# Let's avoid putting crap characters into our urls
# These characters come from http://en.wikipedia.org/wiki/Email_address
ILLEGAL_PROFILE_URL_TRANSLATION_TABLE = {c :' ' for c in '!#$%&\'*+-/=?^_`{|}~."(),:;<>@[\\]'}

profile_question_model_settings = {'QUESTION_MAX_LENGTH': 254}

profile_answer_model_settings = {'CONTENT_MAX_LENGTH': 5000}