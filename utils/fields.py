#Django Imports
from django import forms


class CurrencyField(forms.FloatField):
    """
    This field allows us to handle currencies that are submitted in the format $100,000.00
    Currency symbols, thousands separators, and decimal separators are all removed appropriately
    """

    def to_python(self, value):
        """
        Strip off a $ sign that we would have received from the incoming form data.
        Python's integer field will handle decimal and thousands separators
        """

        if value[0] in ['$']:
            value = value[1:]
        value = value.strip() # AutoNumeric likes to append a currency symbol followed by a space. Strip the space.
        return super(CurrencyField, self).to_python(value)


class StripeAmount(forms.FloatField):
    """
    Stripe forces us to submit our payment values in cents. Maybe trying to save bytes? Unicode thing?
    Convert the cents value to a readable currency when the data is loaded
    """

    def to_python(self, value):
        """
        Strip off a $ sign that we would have received from the incoming form data.
        Python's integer field will handle decimal and thousands separators
        """

        if value[0] in ['$']: # Probably not needed, but just being cautious
            value = value[1:]
        value = value.strip() # Also probably not needed, but just being cautious

        # Convert the cents value to a float with a decimal point
        value = float(value[:-2] + '.' + value[-2:])

        return super(CurrencyField, self).to_python(value)