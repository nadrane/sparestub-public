from django.template import Library
from django.template.defaultfilters import stringfilter
from django.contrib.humanize.templatetags.humanize import intcomma

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
    dollars = round(float(dollars), 2)
    return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])