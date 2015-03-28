from django.core.management.base import BaseCommand
from django.conf import settings
from compressor.cache import flush_offline_manifest

class Command(BaseCommand):
    help = 'Flushes the compressor cache/offline manifest.'

    def handle(self, *args, **options):
        print("Flushing offline manifest...")
        flush_offline_manifest()