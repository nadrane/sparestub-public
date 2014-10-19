__author__ = 'nicholasdrane'

import csv
import logging
import json
from optparse import make_option
from collections import namedtuple

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from locations.models import Location, Alias
from locations.models import calculate_distance_between_zip_codes

from locations.settings import TICKET_DISTANCE_CHOICES

class Command(BaseCommand):
    help = 'Recalculates the zipcode information using the inputted file or zip_code_database.csv'

    option_list = BaseCommand.option_list + (
        make_option('-i', '--inputfile',
                    dest='input_file',
                    default=settings.DEFAULT_ZIP_CODE_CSV,
                    help="The file path to the csv containing zipcode information"),

        make_option('-o', '--outputfile',
                    dest='output_file',
                    default=settings.DEFAULT_ZIP_CODE_JSON,
                    help="The file path to the to the JSON file the script produces."),

        make_option('-c', '--commit',
                    dest='commit_to_db',
                    help="Should we commit the locations in the file to the database?"),

        make_option('-d', '--distance',
                    dest='calculate_distance',
                    help="Should we calculate distances between cities and populate them in the JSON file?"),
    )

    def handle(self, *args, **options):
        self.input_file = options.get('input_file')
        self.output_file = options.get('output_file')
        self.calculate_distance = options.get('calculate_distance')
        self.commit_to_db = options.get('commit_to_db')

        if self.calculate_distance and not (self.output_file and self.input_file):
            raise Exception('An output file is needed to calculate distances for storage.')

        location_list, alias_list = self.read_zip_codes()

        if self.commit_to_db:
            self.update_db(location_list, alias_list)

        if self.calculate_distance:
            distance_dict = self.calculate_distances(location_list)
            self.write_json_file(distance_dict)

    def read_zip_codes(self):
        location_list = []
        alias_list = []
        Location = namedtuple('Location', ['zip_code', 'latitude', 'longitude', 'primary_city', 'state'])
        Alias = namedtuple('Alias', ['zip_code', 'name'])

        try:
            # get a csv reader
            reader = csv.reader(open(self.input_file))
            for (zip_code, mail_type, primary_city, aliases, unacceptable_cities, state, county, timezone, area_codes,
                 latitude, longitude, world_region, country, decommissioned, estimated_population, notes) in reader:

                # Do not handle any zip codes outside of the US
                if country != 'US':
                    logging.debug('line #{}: country equal to {}'.format(reader.line_num, country))
                    continue

                # Do not handle military zip codes
                if mail_type == 'MILITARY':
                    logging.debug('line #{}: country equal to {}'.format(reader.line_num, mail_type))
                    continue

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
                    primary_city = primary_city.strip()
                else:
                    logging.error('line #{}: primary_city not present.'.format(reader.line_num))

                if not state:
                    logging.error('line #{}: state not present.'.format(reader.line_num))

                if not county:
                    logging.warning('line #{}: county not present.'.format(reader.line_num))

                if aliases:
                    aliases = [city.strip() for city in aliases.split()]
                    for name in [primary_city, aliases]:
                        alias = Alias(zip_code, name)
                        alias_list.append(alias)

                location = Location(zip_code, latitude, longitude, primary_city, state)
                location_list.append(location)

        except:
            logging.error('major error', exc_info=True, stack_info=True)

        return location_list, alias_list

    @staticmethod
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

            print('Evaluating zip code {} with {}'.format(location1.zip_code, location2.zip_code))

        return distance_dict

    @staticmethod
    def update_db(locations, aliases):
        for location in locations:
            new_location_entry = Location(zip_code=location.zip_code,
                                          latitude=location.latitude,
                                          longitude=location.longitude,
                                          city=location.primary_city,
                                          state=location.state
                                          )
            logging.debug('Saving {} to the database'.format(location))
            new_location_entry.save()

        for alias in aliases:
            new_alias_entry = Alias(location=Location.objects.filter(zip_code=alias.zip_code),
                                    alias=alias.name
                                    )
            logging.debug('Saving {} to the database'.format(alias))
            new_alias_entry.save()

    def write_json_file(self, distance_dict):
        try:
            json_handler = open(self.output_file, 'wt')
            json.dump(distance_dict, json_handler)
        except Exception:
            pass

