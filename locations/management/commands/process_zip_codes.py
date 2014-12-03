__author__ = 'nicholasdrane'

import csv
import logging
import json
from optparse import make_option
from collections import namedtuple
import boto
from io import StringIO

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.utils import DataError

from locations.models import Location, Alias
from locations.models import calculate_distance_between_zip_codes

from locations.settings import TICKET_DISTANCE_CHOICES, states_abbreviation_list

from locations.models import map_citystate_to_location

class Command(BaseCommand):
    help = 'Recalculates the zipcode information using the inputted file or zip_code_database.csv'

    option_list = BaseCommand.option_list + (
        make_option('-i', '--inputfile',
                    type='string',
                    dest='input_file',
                    default=settings.DEFAULT_ZIP_CODE_CSV,
                    help="The file path to the csv containing zipcode information"),

        make_option('-c', '--commit',
                    action='store_true',
                    dest='commit_to_db',
                    help="Should we commit the locations in the file to the database?"),

        make_option('-d', '--distance',
                    action='store_true',
                    dest='calculate_distance',
                    help="Should we calculate distances between cities and populate them in the JSON file?"),

        make_option('--distance_file',
                    type='string',
                    dest='distance_json_file',
                    default=settings.DEFAULT_ZIP_CODE_JSON,
                    help="The file path to the to the JSON file the script produces."),

        make_option('-y', '--city',
                    action='store_true',
                    dest='calculate_cities',
                    help="Should we determine all existing cities and populate them in the JSON file?"),

        make_option('--city_file',
                    type='string',
                    dest='city_list_json_file',
                    default=settings.DEFAULT_CITY_LIST_JSON,
                    help="The file path to the to the JSON file the city list will be stored in."),
    )

    def handle(self, *args, **options):
        self.AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
        self.AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
        self.AWS_STORAGE_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME

        self.input_file = options.get('input_file')
        self.distance_json_file = options.get('distance_json_file')
        self.calculate_distance = options.get('calculate_distance')
        self.commit_to_db = options.get('commit_to_db')
        self.calculate_cities = options.get('calculate_cities')
        self.city_list_json_file = options.get('city_list_json_file')

        if self.calculate_distance and not (self.distance_json_file and self.input_file):
            raise Exception('An output file is needed to calculate distances for storage.')

        if self.calculate_cities and not (self.city_list_json_file and self.input_file):
            raise Exception('An output file is needed to calculate distances for storage.')

        location_list, alias_list = self.read_zip_codes()

        if self.calculate_cities:
            self.make_city_list(location_list, alias_list)

        if self.commit_to_db:
            self.update_db(location_list, alias_list)

        if self.calculate_distance:
            self.calculate_distances(location_list)

    def make_city_list(self, location_list, alias_list):
        output = {}
        formatted_output = []
        #location_set = set([(location.primary_city, location.state) for location in location_list])
        #alias_set = set([(alias.name, alias.state) for alias in alias_list])
        for loc in location_list:
            if (loc.primary_city, loc.state) not in output:
                output[(loc.primary_city, loc.state)] = [loc.estimated_population, loc.zip_code]
                logging.debug('Adding location {}'.format(loc))
            else:
                if loc.estimated_population > output[(loc.primary_city, loc.state)][0]:
                    logging.debug('Replacing location city/state {} - {} with {}'
                                  .format((loc.primary_city, loc.state),
                                          output[(loc.primary_city, loc.state)], loc))
                    output[(loc.primary_city, loc.state)] = [loc.estimated_population, loc.zip_code]

        for loc in alias_list:
            if (loc.name, loc.state) not in output:
                output[(loc.name, loc.state)] = [loc.estimated_population, loc.zip_code]
                logging.debug('Adding location {}'.format(loc))
            else:
                if loc.estimated_population > output[(loc.name, loc.state)][0]:
                    logging.debug('Replacing location city/state {} - {} with {}'
                                  .format((loc.name, loc.state),
                                           output[(loc.name, loc.state)], loc))
                    output[(loc.name, loc.state)] = [loc.estimated_population, loc.zip_code]

        # Format this into something JSON can understand.
        # Above, we have dicts with tuple keys. JSON only supports string keys
        for k1, k2 in output:

            #If this test passes, we really don't need to include zipcode in the output file seeing as we can just use
            # map_citystate_to_location to recover the zip.
            # This will make the file quite a bit shorter
            #if map_citystate_to_location(k1, k2).zip_code != str(output[(k1, k2)][1]):
            #    if int(output[(k1, k2)][0]) != 0:
            #        print(str(map_citystate_to_location(k1, k2).zip_code) + " " + str(output[(k1, k2)][1]))

            # Capitalize cities and upper case states. This is how the data will appear to the user.
            formatted_output.append([k1.title(), k2.upper(), output[(k1, k2)][0]])

        import pdb
        pdb.set_trace()

        self.write_json_file(formatted_output, self.city_list_json_file)

    def read_zip_codes(self):
        location_list = []
        alias_list = []
        same_city_state = []

        # Note that these shadow the imported Alias and Location objects form within this function scope!
        Location = namedtuple('Location', ['line_no', 'zip_code', 'latitude', 'longitude', 'primary_city', 'state',
                                           'estimated_population', 'timezone'])
        Alias = namedtuple('Alias', ['zip_code', 'name', 'state', 'estimated_population'])

        city_state_combos = {}

        try:
            reader = csv.reader(open(self.input_file))
        # If the file isn't available locally, get it from s3
        except:
            bucket, key = self.open_s3()
            key.key = 'static_root/locations/csv/zip_code_database.csv'

            # Handle everything in memory
            csv_file = key.get_contents_as_string().decode("utf-8")  #get_contents_as_string() is actually returning a bytes object
            reader = csv.reader(StringIO(csv_file)) # csv.reader cannot take a string! It needs a file object

        for (zip_code, mail_type, primary_city, aliases, unacceptable_cities, state, county, timezone, area_codes,
             latitude, longitude, world_region, country, decommissioned, estimated_population, notes) in reader:

            # Skip the line containing the column definitions
            if reader.line_num == 1:
                continue

            # Do not handle any zip codes outside of the US
            if country != 'US':
                logging.debug('line #{}: country equal to {}'.format(reader.line_num, country))
                continue

            # Do not handle military zip codes
            if mail_type == 'MILITARY':
                logging.debug('line #{}: country equal to {}'.format(reader.line_num, mail_type))
                continue

            if state not in states_abbreviation_list:
                logging.debug('line #{}: state equal to {}'.format(reader.line_num, state))
                continue
            else:
                # All strings in the database are lowercase. Let's work with lowercase from the beginning.
                state = state.lower()

            if latitude:
                latitude = float(latitude)
            else:
                logging.error('line #{}: Latitude not present.'.format(reader.line_num))
            if longitude:
                longitude = float(longitude)
            else:
                logging.error('line #{}: longitude not present.'.format(reader.line_num))

            if not zip_code:
                logging.error('line #{}: zipcode not present.'.format(reader.line_num))

            if primary_city:
                # All strings in the database are lowercase. Let's work with lowercase from the beginning.
                primary_city = primary_city.strip().lower()
            else:
                logging.error('line #{}: primary_city not present.'.format(reader.line_num))

            if not county:
                logging.debug('line #{}: county not present.'.format(reader.line_num))

            if not timezone:
                logging.error('line #{}: timezone not present for zipcode {}'.format(reader.line_num, zip_code))
                continue

            if estimated_population:
                estimated_population = int(estimated_population)
            else:
                logging.debug('line #{}: estimated populated not present. Marking as 0'.format(reader.line_num))
                estimated_population = 0

            if aliases:
                aliases = [city.strip().lower() for city in aliases.split(',')]
                for name in aliases:
                    alias = Alias(zip_code, name, state, estimated_population=estimated_population)
                    alias_list.append(alias)

            location = Location(reader.line_num, zip_code, latitude, longitude,
                                primary_city, state, estimated_population, timezone)
            location_list.append(location)

            if not (primary_city, state) in city_state_combos:
                city_state_combos[(primary_city, state)] = location
            else:
                location1 = city_state_combos[(primary_city, state)]
                location2 = Location(line_no=reader.line_num, latitude=latitude, longitude=longitude,
                                     primary_city=primary_city, state=state, zip_code=zip_code,
                                     estimated_population=estimated_population, timezone=timezone)

                if (location1.latitude, location1.longitude) != (location2.latitude, location2.longitude):

                        distance_apart = calculate_distance_between_zip_codes(location1, location2)

                        if distance_apart > 10:
                            same_city_state.append((distance_apart, location1, location2))

        if same_city_state:
            same_city_state = sorted(same_city_state, key=lambda loc: loc[0])
            for match in same_city_state:
                logging.critical('{distance:.2f}\n     {loc1}\n     {loc2}\n\n'.format(distance=match[0],
                                                                                       loc1=match[1],
                                                                                       loc2=match[2]))

        return location_list, alias_list

    def calculate_distances(self, location_list):
        '''
        We allow users to look for tickets that are within x miles of their location.
        Every user and every ticket will have an associated Location record, and every Location record has a latitude
        and a longitude.
        This function calculates the distance between every location record in the system and indexes them based on
        whether they are less than the distance defined in TICKET_DISTANCE_CHOICES.
        '''
        distance_dict = {}
        # The index is included so that we don't do every comparison twice. Obviously the distance between x and y is
        # the same distance between y and x.

        for index, location1 in enumerate(location_list):
            for location2 in location_list[index + 1:]:
                try:
                    distance = calculate_distance_between_zip_codes(location1, location2)
                except ValueError:
                    return
                for radius in TICKET_DISTANCE_CHOICES:
                    if distance <= radius:
                        if location1.zip_code in distance_dict:
                            if radius in distance_dict[location1.zip_code]:
                                distance_dict[location1.zip_code][radius].append(location2.zip_code)
                            else:
                                distance_dict[location1.zip_code] = {radius: [location2.zip_code]}
                        else:
                            distance_dict[location1.zip_code] = {radius: [location2.zip_code]}
                        if location2.zip_code in distance_dict:
                            if radius in distance_dict[location2.zip_code]:
                                distance_dict[location2.zip_code][radius].append(location1.zip_code)
                            else:
                                distance_dict[location2.zip_code] = {radius: [location1.zip_code]}
                        else:
                            distance_dict[location2.zip_code] = {radius: [location1.zip_code]}

            logging.debug('Evaluating zip code {} with {}'.format(location1.zip_code, location2.zip_code))

        self.write_json_file(distance_dict, self.output_file)

    @staticmethod
    def update_db(locations, aliases):
        for location in locations:
            new_location_entry = Location(zip_code=location.zip_code,
                                          latitude=location.latitude,
                                          longitude=location.longitude,
                                          city=location.primary_city,
                                          state=location.state,
                                          population=location.estimated_population,
                                          timezone=location.timezone
                                          )
            logging.debug('Saving {} to the database'.format(location))
            new_location_entry.save()

        for alias in aliases:

            new_alias_entry = Alias(location=Location.objects.filter(zip_code=alias.zip_code)[0],
                                    alias=alias.name
                                    )

            logging.debug('Saving {} to the database'.format(alias))
            try:
                new_alias_entry.save()

            # triggered when the input does not match the datatype of the field (eg., too many characters for VARCHAR)
            except DataError:
                logging.critical('Failed to enter alias: {} into the database'.format(alias),
                                 exc_info=True,
                                 stack_info=True)

    @staticmethod
    def write_json_file(output_dict, fp):
        try:
            json_handler = open(fp, 'wt')
            json.dump(output_dict, json_handler)
        except Exception:
            pass

    def open_s3(self):
        """
        Opens connection to S3 returning bucket and key
        """
        conn = boto.connect_s3(
            self.AWS_ACCESS_KEY_ID,
            self.AWS_SECRET_ACCESS_KEY,
            )
        try:
            bucket = conn.get_bucket(self.AWS_STORAGE_BUCKET_NAME)
        except boto.exception.S3ResponseError:
            bucket = conn.create_bucket(self.AWS_STORAGE_BUCKET_NAME)
        return bucket, boto.s3.key.Key(bucket)
