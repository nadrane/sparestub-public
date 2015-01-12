# Django core modules
from datetime import date

def calculate_age(birthdate):
    """
    Calculate a users age as of today.
    """

    if birthdate:
        today = date.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return None
