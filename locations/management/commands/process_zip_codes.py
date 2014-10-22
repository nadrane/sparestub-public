__author__ = 'nicholasdrane'

import csv
import logging
import json
from optparse import make_option
from collections import namedtuple

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.utils import DataError

from locations.models import Location, Alias
from locations.models import calculate_distance_between_zip_codes

from locations.settings import TICKET_DISTANCE_CHOICES, states_abbreviation_list


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
                    default='False',
                    help="Should we commit the locations in the file to the database?"),

        make_option('-d', '--distance',
                    dest='calculate_distance',
                    default='False',
                    help="Should we calculate distances between cities and populate them in the JSON file?"),

        make_option('-y', '--city',
                    dest='calculate_cities',
                    default='True',
                    help="Should we determine all existing cities and populate them in the JSON file?"),
    )

    def handle(self, *args, **options):
        import pdb
        pdb.set_trace()
        self.input_file = options.get('input_file')
        self.output_file = options.get('output_file')
        self.calculate_distance = options.get('calculate_distance').lower().find('true')
        self.commit_to_db = options.get('commit_to_db').lower().find('true')
        self.calculate_cities = options.get('calculate_cities').lower().find('true')

        if self.calculate_distance and not (self.output_file and self.input_file):
            raise Exception('An output file is needed to calculate distances for storage.')

        location_list, alias_list = self.read_zip_codes()

        output_dict = {}

        if self.calculate_cities:
            output_dict = self.make_city_list(location_list, alias_list, output_dict)

        #TODO why is this getting set as a string at the command prompt

        if self.commit_to_db:
            self.update_db(location_list, alias_list)

        if self.calculate_distance:
            output_dict = self.calculate_distances(location_list)

        if output_dict:
            self.write_json_file(output_dict)

    def make_city_list(self, location_list, alias_list, output_dict):
        output_dict['city'] = []
        location_set = set([(location.primary_city, location.state) for location in location_list])
        alias_set = set([(alias.name, alias.state) for alias in alias_list])
        for place in location_set.union(alias_set):
            output_dict['city'].append(place)

        return output_dict

    def read_zip_codes(self):
        location_list = []
        alias_list = []
        same_city_state = []
        Location = namedtuple('Location', ['line_no', 'zip_code', 'latitude', 'longitude', 'primary_city', 'state',
                                           'estimated_population'])
        Alias = namedtuple('Alias', ['zip_code', 'name', 'state'])

        city_state_combos = {}
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

                if state not in states_abbreviation_list:
                    logging.debug('line #{}: state equal to {}'.format(reader.line_num, state))
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
                    logging.debug('line #{}: county not present.'.format(reader.line_num))

                if aliases:
                    aliases = [city.strip() for city in aliases.split()]
                    for name in aliases:
                        alias = Alias(zip_code, name, state)
                        alias_list.append(alias)

                location = Location(reader.line_num, zip_code, latitude, longitude,
                                    primary_city, state, estimated_population)
                location_list.append(location)

                if not (primary_city, state) in city_state_combos:
                    city_state_combos[(primary_city, state)] = location
                else:
                    location1 = city_state_combos[(primary_city, state)]
                    location2 = Location(line_no=reader.line_num, latitude=latitude, longitude=longitude,
                                         primary_city=primary_city, state=state, zip_code=zip_code,
                                         estimated_population=estimated_population)

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

            logging.debug('Evaluating zip code {} with {}'.format(location1.zip_code, location2.zip_code))

        return distance_dict

    @staticmethod
    def update_db(locations, aliases):
        for location in locations:
            new_location_entry = Location(zip_code=location.zip_code,
                                          latitude=location.latitude,
                                          longitude=location.longitude,
                                          city=location.primary_city,
                                          state=location.state,
                                          population=location.estimated_population
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

    def write_json_file(self, output_dict):
        try:
            json_handler = open(self.output_file, 'wt')
            json.dump(output_dict, json_handler)
        except Exception:
            pass

