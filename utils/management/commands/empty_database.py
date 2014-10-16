__author__ = 'nicholasdrane'


import psycopg2
from optparse import make_option

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from utils.miscellaneous import get_variable_from_settings

class Command(BaseCommand):
    help = 'Completely wipes out the sparestub database.'

    def handle(self, *args, **options):
        self.recreate_empty_database()


    def recreate_empty_database(self):

        # We must always be connected to some database to perform SQL commands.
        databases = get_variable_from_settings('DATABASES')
        database_to_drop = databases.get('default').get('NAME')
        password = databases.get('default').get('PASSWORD')

        with psycopg2.connect(database="postgres", user="postgres", password=password) as conn:  #http://stackoverflow.com/questions/19426448/creating-a-postgresql-db-using-psycopg2
            with conn.cursor() as cur:
                conn.autocommit = True   #  Explains why we do this - we cannot drop or create from within a DB transaction. http://initd.org/psycopg/docs/connection.html#connection.autocommit
                try:
                    cur.execute('DROP DATABASE {};'.format(database_to_drop))
                except psycopg2.ProgrammingError: # Thrown if crowdsurfer DB does not exist
                    pass
                cur.execute('CREATE DATABASE {};'.format(database_to_drop))

        # Recreate the tables in the database according to our models
        call_command('syncdb', interactive=False)

        # Create the cache table for DB queries
        call_command('createcachetable', 'cache_table', interactive=False)
        return