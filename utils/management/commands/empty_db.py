import logging
import psycopg2

from django.core.management import call_command
from django.core.management.base import BaseCommand

from utils.miscellaneous import get_variable_from_settings
from django.conf import settings


class Command(BaseCommand):
    help = 'Completely wipes out the sparestub database.'

    def handle(self, *args, **options):

        # We must always be connected to some database to perform SQL commands.
        databases = get_variable_from_settings('DATABASES')
        self.database_to_drop = databases.get('default').get('NAME')
        self.password = databases.get('default').get('PASSWORD')
        self.ignore = ['locations_location', 'locations_alias']  # Tables that we do not want to drop

        self.recreate_empty_database()

    def recreate_empty_database(self):
        database = settings.DATABASES['default']
        with psycopg2.connect(database=database['NAME'],
                              user=database['USER'],
                              password=database['PASSWORD'],
                              host=database['HOST'],
                              port=database['PORT']
                              ) as conn:  #http://stackoverflow.com/questions/19426448/creating-a-postgresql-db-using-psycopg2
            with conn.cursor() as cur:
                conn.autocommit = True   #  Explains why we do this - we cannot drop or create from within a DB transaction. http://initd.org/psycopg/docs/connection.html#connection.autocommit
                try:
                    # Get a list of all tables in database
                    cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
                    for table in cur.fetchall():
                        table = table[0]
                        # Skip tables that require a lot of pre-processing that do not change often
                        if table in self.ignore:
                            continue
                        cur.execute('DROP TABLE {} CASCADE;'.format(table))
                except psycopg2.ProgrammingError as e:
                    logging.warning('Failed to drop table {}'.format(table), exc_info=True, stack_info=True)

        # Recreate the tables in the database according to our models
        call_command('syncdb', interactive=False)