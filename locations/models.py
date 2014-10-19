# Standard imports
import math
import logging

# Django core imports
from django.db import models
from .settings import location_settings

# SpareStub imports
from utils.miscellaneous import reverse_category_lookup

DEGREES_TO_RADS = math.pi/180.0
SIN = math.sin
COS = math.cos
ACOS = math.acos


class Location(models.Model):
    zip_code = models.CharField(max_length=5)  # TODO Maybe specify min length too

    latitude = models.DecimalField(max_digits=5,
                                   decimal_places=2
                                   )

    longitude = models.DecimalField(max_digits=5,
                                    decimal_places=2
                                    )

    city = models.CharField(max_length=location_settings.get('CITY_MAX_LENGTH'),
                            db_index=True,
                            )

    state = models.CharField(max_length=2)

    def __str__(self):
        return '{} -- {} {}'.format(self.zipcode, self.lat, self.lon)


class Alias(models.Model):
    location = models.ForeignKey(Location)

    # This alias is going to be the name of a city
    alias = models.CharField(max_length=location_settings.get('CITY_MAX_LENGTH'),
                             db_index=True,
                             )


def get_state_name(state_abbreviation):
    return reverse_category_lookup(state_abbreviation, location_settings.get('STATES'))


def calculate_distance_between_zip_codes(location1, location2):
        """
        Takes two locations and used their latitudes and longitudes to calculates the distance between them in miles.
        """
        lat1, long1 = location1.latitude, location1.longitude
        lat2, long2 = location2.latitude, location2.longitude

        # phi = 90 - latitude
        phi1 = (90.0 - lat1) * DEGREES_TO_RADS
        phi2 = (90.0 - lat2) * DEGREES_TO_RADS

        # theta = longitude
        theta1 = long1 * DEGREES_TO_RADS
        theta2 = long2 * DEGREES_TO_RADS

        # Compute spherical distance from spherical coordinates.

        # For two locations in spherical coordinates
        # (1, theta, phi) and (1, theta, phi)
        # cosine( arc length ) =
        #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
        # distance = rho * arc length

        try:
            cos = SIN(phi1) * SIN(phi2) * COS(theta1 - theta2) + COS(phi1) * COS(phi2)


            # Some floating point rounding errors are causing cos to be greater than 1
            # We don't need needle percisio, so magic the problem away.
            if cos > 1:
                cos = 1.0

            arc = ACOS(cos)

        except ValueError:
            logging.error('fatal error', exc_info=True, stack_info=True)

        # Multiply by the radius of the earth in miles
        return arc * 3963.1676