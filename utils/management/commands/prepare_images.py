import os
import logging
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

                    save_extension = None
                    if file_extension in ('.jpeg', '.jpg'):
                        save_extension = 'JPEG'

                    elif file_extension == '.png':
                        save_extension = 'PNG'

                    else:
                        continue

                    filename = os.path.join(current_directory, file)
                    new_filename = os.path.join(current_directory, 'resized_' + file)

                    try:
                        image = Image.open(filename)
                        current_size = image.size
                        if current_size[0] > 1000:
                            image = image.resize((int(current_size[0] / 2), int(current_size[1] / 2)))
                        image.save(new_filename, save_extension)
                        if save_extension == 'JPEG':
                            subprocess.call(['/Users/nicholasdrane/Documents/coding/sparestub/cjpeg-mozjpeg3-mac/cjpeg',
                                             '-verbose',
                                             "-outfile",
                                             filename,
                                             new_filename])
                        else:
                            subprocess.call(['/Users/nicholasdrane/Documents/coding/sparestub/pngquant/pngquant',
                                             '--verbose',
                                             new_filename,
                                             '-o',
                                             filename,
                                             '--speed',
                                             '1',
                                             '-f'])

                    except OSError:
                        logging.error('Failed to load {} for compression and resizing'.format(file))

