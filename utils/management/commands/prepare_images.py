import os
import subprocess
from PIL import Image

from django.core.management.base import BaseCommand

from django.conf import settings


class Command(BaseCommand):
    help = 'Completely wipes out the sparestub database.'

    def handle(self, *args, **options):
        self.DIRECTORIES = [settings.STATIC_ROOT]
        for root_directory in self.DIRECTORIES:
            for current_directory, sub_directories, files in os.walk(root_directory):
                #os.walk returns a tuple containing 3 items:
                    # 1. the directory that it is currently analyzing
                    # 2. A list containing the sub-directories within current_directory
                    # 3. A list containing the files within that current_directory
                for file in files:
                    file_name, file_extension = os.path.splitext(file)
                    # These files need to be resized and compressed
                    if file_extension  in ('.jpeg', '.png', 'jpg'):
                        continue

                    import pdb
                    pdb.set_trace()

                    filename = os.path.join(current_directory, file)
                    image = Image(filename)
                    image = Image.resize((500, 500))
                    Image.save(filename, 'jpeg')
