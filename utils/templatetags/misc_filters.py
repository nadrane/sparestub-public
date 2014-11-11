from django.template import Library

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