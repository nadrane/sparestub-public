__author__ = 'nicholasdrane'
import unittest

from collections import namedtuple
from django.test import TestCase
from .models import calculate_distance_between_zip_codes


class DistanceTestCase(TestCase):

    def setUp(self):
        pass

    def correct_distances(self):
        Location = namedtuple('Location', ['zip_code', 'latitude', 'longitude', 'primary_city', 'state'])
        Alias = namedtuple('Alias', ['zip_code', 'name'])

        zip_code1 = Location(zip_code='17309', latitude=39.86, longitude=-76.45, primary_city='Brogue', state='PA')
        zip_code2 = Location(zip_code='15468', latitude=39.9, longitude=-76.79, primary_city='New Salem', state='PA')
