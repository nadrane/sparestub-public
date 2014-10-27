#Django Imports
from django import forms


class CurrencyField(forms.FloatField):

    def to_python(self, value):
        '''
        Strip off a $ sign that we would have received from the incoming form data.
        Python's integer field will handle decimal and thousands separators
        '''
        if value[0] in ['$']:
            value = value[1:]
        value = value.strip() # AutoNumeric likes to append a currency symbol followed by a space. Strip the space.
        return super(CurrencyField, self).to_python(value)