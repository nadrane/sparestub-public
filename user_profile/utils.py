__author__ = 'nicholasdrane'

from datetime import date

def calculate_age(born):
    '''
    Thanks Stackoverflow! http://stackoverflow.com/questions/2217488/age-from-birthdate-in-python/9754466#9754466
    '''
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))