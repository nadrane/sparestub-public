# Standard imports
import math
import logging
import re

# Django core imports
from django.db import models
from .settings import location_settings
from django.forms import ValidationError

# SpareStub imports
from utils.miscellaneous import reverse_category_lookup

DEGREES_TO_RADS = math.pi/180.0
SIN = math.sin
COS = math.cos
ACOS = math.acos


class LocationMatchingException(Exception):

    def __init__(self, msg):
        self.msg = msg

        super(Exception, self).__init__()


class Location(models.Model):
    zip_code = models.CharField(primary_key=True,
                                max_length=5,
                                db_index=True,
                                unique=True,
                                )

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

    population = models.IntegerField()

    timezone = models.CharField(max_length=50)

    def __str__(self):
        return '{}, {}'.format(self.city.title(), self.state.upper(), self.zip_code)

    @staticmethod
    def valid_zipcode(zip_code):
        if not re.match('^\d{5}$', zip_code):
            raise ValidationError('That zipcode is not formatted correctly', code="invalid_zipcode_format")
        zip_code = Location.objects.filter(zip_code=zip_code)
        if not zip_code:
            raise ValidationError('The submitted zip code does not match a real zip code', code="invalid_zipcode")
        return zip_code


class Alias(models.Model):
    #TODO should we link to the location table, or should it link back in a many to one relationship?
    location = models.ForeignKey(Location)

    # This alias is going to be the name of a city
    alias = models.CharField(max_length=location_settings.get('CITY_MAX_LENGTH'),
                             db_index=True,
                             )

    def __str__(self):
        return 'alias: {}, location: {}'.format(self.alias, self.location)


def map_citystate_to_location(city, state):
    '''
    We need to map the city and state to an entry in the location table.
    This is actually more difficult than it should be. I'm going to copy and paste an excerpt from an email in here
    that describes the problem.

    We have users identify their location with a zip code at registration.  Every zip code is associated with a
    primary city, some aliases (like Manhattan for new york, ny), a latitude and longitude, and bunch of other
    data. Turns out zip codes are not based on geography but rather a system devised by USPS for efficient
    distribution of mail. Therefore, it’s possible for people in the same zip code to live across the country
    for one another. Fortunately, this is mostly a military thing. Suffice to say, zip codes are not terribly
    indicative of geographic location.

    When we ask users to submit a ticket, we ask for a location of the event. We aren’t going to ask for a zip
    code. This location is a city/state combination, and each pair needs to be mapped back to a zip code and its
    associated latitude and longitude. This would be pretty straightforward except that there are A LOT of
    instances where two distinct zip code's coordinates differ by as much as 50 miles geographically,
    even though they map to the same city and state. So when a user submits their ticket,
    which zip code do we map to?  Probably the one in the more populous area, since it’s most likely the
    location of the event.

    returns: The best location match for a city/state combination.
             Raises LocationMatchingExceptom on invalid input
    '''
    '''

    # The cities and states in the DB are lowercase. Make sure the input is as well.
    city = city.strip().lower()
    state = state.strip().lower()

    # Filter over location first since it's a large more precise index than state
    location_city_match_list = Location.objects.filter(city=city)

    if location_city_match_list:
        location_citystate_match_list = location_city_match_list.filter(state=state)

        # If we hone in on a single location using just the inputted city and state, we're golden
        if location_citystate_match_list.count() == 1:
            return location_citystate_match_list[0]

        # We we identified a city but the matched location does not match the entered state, then they probably
        # fubbed the state.

        # But they might have selected an alias from a different state. That alias came into this function as city.
        if location_city_match_list and not location_citystate_match_list:
            raise LocationMatchingException("The inputted city exists in the database, but \
                                     it does not match the state entered.")

    # We didn't match a city, but maybe we'll match an alias
    else:
        alias_city_match_list = Alias.objects.filter(alias=city).location

        if alias_city_match_list:
            alias_citystate_match_list = alias_city_match_list.filter(location__state=state)

        # If we hone in on a single location using just the inputted city and state, we're golden
        if alias_citystate_match_list.count() == 1:
            return alias_citystate_match_list[0]

        # We we identified a city but the matched location does not match the entered state, then they probably
        # fubbed the state.
        if alias_city_match_list and not alias_citystate_match_list:
            raise LocationMatchingException("The inputted city exists as an alias in the database,"
                                    " but it does not match the state entered.")

    possible_locations = location_citystate_match_list.append(alias_citystate_match_list)

    # Return the location with the largest population from the set of everything matched
    if possible_locations:
        possible_locations.sort(possible_locations, key=lambda loc: loc.population)
        return possible_locations[0]

    if not possible_locations:
        raise LocationMatchingException('City name does not match a single city or alias in the database.')

    return
    '''

    '''
        This function is designed pretty specifically work with the input that we expect to get from submit_ticket.js on
        the front end. We might want to use different logic during ticket search. I'll need to ponder that problem.
        Chances are we won't seeing as were are going to use the same JSON file as input to typeahead in the ticket
        search section as we do in the ticket submission section.
    '''
    # The cities and states in the DB are lowercase. Make sure the input is as well.
    city = city.strip().lower()
    state = state.strip().lower()
    match = None  # The location that we are going to return

    # Filter over location first since it's a large more precise index than state
    location_city_match_list = Location.objects.filter(city=city)

    # Make sure that every matched city also has the inputted state
    if location_city_match_list:
        location_citystate_match_list = location_city_match_list.filter(state=state)

        # We don't need to be working with a query set anymore but rather just a plain old list of Location objects,
        location_citystate_match_list = [location for location in location_citystate_match_list]
    else:
        location_citystate_match_list = []

    # Now repeat the same process for aliases
    alias_city_match_list = Alias.objects.filter(alias=city)

    if alias_city_match_list:
        alias_citystate_match_list = alias_city_match_list.filter(location__state=state)
        alias_citystate_match_locations = [alias.location for alias in alias_citystate_match_list]

        # This list will have duplicates if a location has an alias with the same name as it's primary city.
        # But duplicates are fine because we only return one.
        location_citystate_match_list.extend(alias_citystate_match_locations)

    # Return the location with the largest population from the set of everything matched.
    # This is precisely what the user would have selected ont the front end.
    if location_citystate_match_list:
        location_citystate_match_list.sort(key=lambda loc: loc.population)
        match = location_citystate_match_list[-1]  # Return the last entry seeing as sort is in acsending order!

    else:
        raise LocationMatchingException('City name does not match a single city or alias in the database.')

    return match




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