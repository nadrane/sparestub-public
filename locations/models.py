# Standard imports
import math

# Django core imports
from django.db import models

class location(models.Model):
    pass

class Zipcode:
    def __init__(self, zipcode, latitude, longitude, city, state, aliases):
        self.zipcode = zipcode
        self.latitude = latitude
        self.longitude = longitude
        #self.city = city
        #self.state = state
        #self.aliases = aliases if isinstance(aliases, list) else [aliases]

    def __str__(self):
        return '{} -- {} {}'.format(self.zipcode, self.lat, self.lon)


class City:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return '{} -- {} {}'.format(self.city, self.lat, self.lon)


def map_zip_to_city(zipcode):
    return 'Astoria', 'New York'

def get_state_full_name(state_abbreviation):
    pass

def calculate_distance_between_points(lat1, long1, lat2, long2):
    """
    Takes two tuples containing latitude and longitude and calculates the distance between them in miles.
    """
    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) =
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos(cos)

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return arc * 3963.1676