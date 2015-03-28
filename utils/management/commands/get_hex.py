from django.core.management.base import BaseCommand
from django.conf import settings
from compressor.cache import get_offline_hexdigest

class Command(BaseCommand):
    help = 'get_offline_hexdigest'

    def handle(self, *args, **options):
        return get_offline_hexdigest(*args)