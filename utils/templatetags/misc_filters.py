from django.template import Library
from django.template.defaultfilters import stringfilter
from django.contrib.humanize.templatetags.humanize import intcomma
from logentries import LogentriesHandler
import logging
import time

# temp
log = logging.getLogger('logentries')
log.setLevel(logging.INFO)
handler = LogentriesHandler('28379e13-d9b8-434f-a233-7ec9369d2fcb')
log.addHandler(handler)

register = Library()

@register.filter
def get_range(value):
    """
    Returns an iterable list given a integer
    """
    # Handle the case where value is None. Don't just say "if value" in case it is 0.
    if value is not None:
        return range(value)
    return value

# Thank you Stackoverflow for this simple and easy solution
#http://stackoverflow.com/questions/6481788/format-of-timesince-filter
@register.filter(is_safe=True)
@stringfilter
def upto(value, delimiter=None):
    return value.split(delimiter)[0]

@register.filter(is_safe=True)
@stringfilter
def format_stripe_price(value):
    return int(float(value) * 100)

@register.filter(is_safe=True)
def currency(dollars):
    if not dollars :
       log.warn("dollars was null or string empty")
       return dollars
    dollars = round(float(dollars), 2)
    return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])
