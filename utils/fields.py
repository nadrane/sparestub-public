#3rd Party Imports
from pytz import timezone

#Django Imports
from django import forms
from django.utils.timezone import activate

class CurrencyField(forms.FloatField):


    '''
    This field allows us to handle currencies that are submitted in the format $100,000.00
    Currency symbols, thousands separators, and decimal separators are all removed appropriately
    '''
    def to_python(self, value):
        '''
        Strip off a $ sign that we would have received from the incoming form data.
        Python's integer field will handle decimal and thousands separators
        '''
        if value[0] in ['$']:
            value = value[1:]
        value = value.strip() # AutoNumeric likes to append a currency symbol followed by a space. Strip the space.
        return super(CurrencyField, self).to_python(value)