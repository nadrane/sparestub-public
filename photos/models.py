# Standard Python modules
import string
import io
import random
import os
import logging

#Django
from utils.models import TimeStampedModel
from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

# 3rd Party modules
from PIL import Image

# Crowdsurfer modules
from .settings import PHOTO_THUMBAIL_WIDTH, PHOTO_LISTING_DETAIL_WIDTH


def random_photo():
    return Photo.objects.order_by('?')[0]

# Since I cannot figure out how to pass an extra parameter to generate_file_name based on the field it is applied to,
# we can create wrappers around it instead.
def generate_original_file_name(instance, filename):
    return os.path.join('photos/original/', generate_file_name(instance, filename))


def generate_thumbnail_file_name(instance, filename):
    return os.path.join('photos/thumbnail/', generate_file_name(instance, filename))


def generate_detail_file_name(instance, filename):
    return os.path.join('photos/detail/', generate_file_name(instance, filename))


def generate_file_name(instance, filename):
    #No need to worry about duplicate file names. Django appends _n in the case of pre-existing name.
    file_extension = filename[filename.rfind('.'):]
    
    #Generate a list of all digits and upper and lower case letters.
    possible_characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    
    #Select and append into a string 5 random characters from the previous list.
    #Django will append a one to my file string if it is taken, so we do not need to query the database for collisions
    random_string = ''.join(random.choice(possible_characters) for x in range(5))

    return random_string + file_extension


def convert_image_to_django_uploadable(image):

    if image is None:
        return None

    # If we are dealing with a type of PIL.Image
    if isinstance(image, io.BytesIO):
        return InMemoryUploadedFile(image, None, 'temp.jpg', 'image/jpeg', len(image.getvalue()), None)

    else:
        return InMemoryUploadedFile(io.BytesIO(image.tobytes()), None, 'temp.jpg', 'image/jpeg', len(image.tobytes()), None)


def convert_image_string(image_byte_string, file_path=None):
    if not image_byte_string:
        return None

    image_byte_string = convert_to_jpeg(image_byte_string, file_path)

    if not image_byte_string:
        return None

    original_file = convert_image_to_django_uploadable(image_byte_string)
    thumbnail_bytes = make_thumbnail(image_byte_string)
    thumbnail_file = convert_image_to_django_uploadable(thumbnail_bytes)
    detail_bytes = make_detail_photo(image_byte_string)
    detail_file = convert_image_to_django_uploadable(detail_bytes)


    original_file.seek(0)
    thumbnail_file.seek(0)
    detail_file.seek(0)

    return original_file, thumbnail_file, detail_file


def convert_to_jpeg(image_bytes, file_path=None):
    '''
    Take an image of any format and convert it to a jpeg
    '''

    if not image_bytes:
        return None

    try:
        # Make sure that we are reading from the beginning of the file, otherwise Image.open will
        # not be able to determine the file type and will fail.
        image_bytes.seek(0)
        PIL_image = Image.open(image_bytes)

        PIL_image = PIL_image.convert('RGB')
        image_bytes = io.BytesIO()
        PIL_image.save(image_bytes, 'JPEG')
        return image_bytes

    # If Image.open fails, we raise this exception
    except IOError:
        logger = logging.getLogger(__name__)
        #TODO make far more robust error
        if file_path:
            logger.error('Could not convert image %s to jpeg', file_path)
        else:
            logger.error('Could not convert image to jpeg', file_path)
        return None


def resize(image_bytes, new_width_function, new_height_function):
     # This likely means that we failed to get scrap the file from the website
    if not image_bytes:
        return None

    try:
        # Make sure that we are reading from the beginning of the file, otherwise Image.open will
        # not be able to determine the file type and will fail.
        image_bytes.seek(0)
        PIL_image = Image.open(image_bytes)

    # If Image.open fails, we raise this exception
    except IOError:
        logger = logging.getLogger(__name__)
        #TODO make far more robust error
        logger.error('Could not make resize image')
        return None

    current_width, current_height = PIL_image.size

    # The height and width values to scale the thumbnail to
    new_width = new_width_function(current_width, current_height)
    new_height = new_height_function(current_width, current_height)

    # If the image is currently smaller than 236 pixels wide, we need to call Image.resize to scale the image up instead
    if new_width > current_width:
        PIL_image = PIL_image.resize((new_width, new_height), Image.ANTIALIAS)
    # If the image is wider than 236 pixels already, simply scale down using Image.thumbnail
    else:
        PIL_image.thumbnail((new_width, new_height), Image.ANTIALIAS)

    thumbnail_bytes = io.BytesIO()
    PIL_image.save(thumbnail_bytes, 'JPEG')

    return thumbnail_bytes


def make_thumbnail(image_bytes):
    '''
    Takes an Image and scales its size such that the width is equal to PHOTO_THUMBAIL_WIDTH
    '''

    # The height and width values to scale the thumbnail to
    new_width_function = lambda width, height: PHOTO_THUMBAIL_WIDTH
    new_height_function = lambda width, height : int(height * (new_width_function(width, height) / width))

    return resize(image_bytes, new_width_function, new_height_function)


def make_detail_photo(image_bytes):
    '''
    Takes an Image and scales its size such that the width is equal to PHOTO_LSITING_DETAIL_WIDTH
    '''

    # The height and width values to scale the new photo to
    new_width_function = lambda width, height: PHOTO_LISTING_DETAIL_WIDTH if width > PHOTO_LISTING_DETAIL_WIDTH else width
    new_height_function = lambda width, height : int(height * (new_width_function(width, height) / width))

    return resize(image_bytes, new_width_function, new_height_function)


def get_photo_height(image_bytes):
    # This likely means that we failed to get scrap the file from the website
    if not image_bytes:
        return None

    try:
        # Make sure that we are reading from the beginning of the file, otherwise Image.open will
        # not be able to determine the file type and will fail.
        image_bytes.seek(0)
        PIL_image = Image.open(image_bytes)

    # If Image.open fails, we rais/e this exception
    except IOError:
        logger = logging.getLogger(__name__)
        #TODO make far more robust error
        logger.error('Could not get image height')
        return None

    return PIL_image.size[1]


class Photo(TimeStampedModel):

     # If we extract the photo from a URL, the object will probably have a null original_file at the beginning.
     # Basically, we create a stub file record in these cases.
     # Obviously a stub is going to have no data, hence why all the columns are nullable


    thumbnail_file = models.ImageField(upload_to=generate_thumbnail_file_name,  # So that we can use variable in custom methods
                                       null=True,  # We need to generate the thumbnail through a queued job
                                       blank=True
                                       )

    detail_file = models.ImageField(upload_to=generate_detail_file_name,
                                    null=True,
                                    blank=True,
                                    verbose_name='listing detail file',
                                    )

    # Note that the thumbnail photo width is constant and is always equal to PHOTO_THUMBNAIL_WIDTH
    # The height and width are needed for Masonry.
    # We want to be able to format the screen layout even before the photos are transferred to the server.
    thumbnail_height = models.IntegerField(null=True,
                                           blank=True,
                                           )

    original_file = models.ImageField(upload_to=generate_original_file_name,    # Keep the original file around in case we want to store more photo sizes later.
                                      null=True,
                                      blank=True
                                      )

    #TODO Compress the original photo when it is initially stored to something managable. An arbitrrary size won't work.

    #Override the queryset delete method to delete the actual photo files from the file system
    def delete(self):
        #Prevent trying to access undefined variable error if the files truly do not exist on the server
        absolute_original_path = None
        absolute_thumbnail_path = None
        
        #If we are going to delete the file from the database, we need to remove the file from the file system.
        #We need to remove both the thumbnail and the original photo
        if self.thumbnail_file:
            absolute_thumbnail_path = os.path.join(settings.MEDIA_ROOT, str(self.thumbnail_file))
            #Make sure all of the separators (the forward and backward slashes) are aligned correctly
            absolute_thumbnail_path = os.path.normpath(absolute_thumbnail_path)
        if self.original_file:
            absolute_original_path = os.path.join(settings.MEDIA_ROOT, str(self.original_file))
            #Make sure all of the separators (the forward and backward slashes) are aligned correctly
            absolute_original_path = os.path.normpath(absolute_original_path)
        
        if absolute_thumbnail_path and os.path.isfile(absolute_thumbnail_path):
            os.remove(absolute_thumbnail_path)
        
        if absolute_original_path and os.path.isfile(absolute_original_path): 
            os.remove(absolute_original_path)
        
        #Actually delete the Photo object from the DB
        super(Photo, self).delete()

    def __unicode__(self):
        return u"Photo of %s" % (self.user)
