__author__ = 'nicholasdrane'

import csv
import logging
import json

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from locations.models import Zipcode, City


class Command(BaseCommand):
    help = 'Recalculates the zipcode information using the inputted file or zip_code_database.csv'

    make_option('-i', '--inputfile',
                dest='input_file',
                default=settings.ZIPCODE_CSV,
                help="The file path to the csv containing zipcode information"),

    make_option('-o', '--outputfile',
                dest='output_file',
                default=settings.ZIPCODE_JSON,
                help="The file path to the to the JSON file the script produces."),

    def handler(self):
        zipcode_list = self.process_upload()
        distance_dict = self.calculate_distances(zipcode_list)
        self.write_json_file(distance_dict)

    def process_upload(self):
        zipcode_list = []
        city_list = []

        try:
            # get a csv reader
            reader = csv.reader(open(self.input_file))
            for (zipcode, type, primary_city, aliases, unacceptable_cities, state, county, timezone, latitude,
                 longitude, world_region, country, decommissioned, estimated_population, notes) in reader:

                if latitude:
                    latitude = float(latitude)
                else:
                    logging.error('line #{}: Latitude not present.'.format(reader.line_num))
                if longitude:
                    longitude = float(longitude)
                else:
                    logging.error('line #{}: longitude not present.'.format(reader.line_num))

                if not zipcode:
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

                zipcode = Zipcode(zipcode, latitude, longitude)


                for x in [primary_city, aliases]:
                    city = City(primary_city, latitude, longitude)
                    city_list.append(city)

                zipcode_list.append(zipcode)
                city_list.append

        except:
            logging.critical('major error')

        return zipcode_list

    def calculate_distance(self, zipcode_list):
        for zipcode1 in zipcode_list:
            for zipcode2 in zipcode_list:
                pass

    def write_json_file(self, zipcode_list):
        try:
            json_handler = open(self.output_file)
            json.dump(zipcode_list, json_handler)
        except Exception:
            pass

