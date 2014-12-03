# Standard Python Imports
import string
import io
import random
import os
import logging
import math

#Django Imports
from utils.models import TimeStampedModel
from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

# 3rd Party Imports
from PIL import Image

# SpareStub Imports
from .settings import PROFILE_THUMBNAIL_HEIGHT, SEARCH_THUMBNAIL_HEIGHT


def generate_original_file_name(instance, filename):
    return os.path.join('photos', 'original', generate_file_name(instance, filename))


def generate_search_thumbnail_name(instance, filename):
    return os.path.join('photos', 'search', generate_file_name(instance, filename))


def generate_profile_thumbnail_file_name(instance, filename):
    return os.path.join('photos', 'profile', generate_file_name(instance, filename))


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
    return InMemoryUploadedFile(image, None, 'temp.jpg', 'image/jpeg', len(image.getvalue()), None)

def convert_image_string(image_byte_string, crop_coords=None, crop_width=None, crop_height=None):
    import pdb
    pdb.set_trace()
    if not image_byte_string:
        return None

    try:
        pil_image = Image.open(image_byte_string)
    # If Image.open fails, we raise this exception
    except IOError:
        logging.error('Could not convert image %s to jpeg', exc_info=True, stack_info=True)
        return None

    pil_image = crop_photo(pil_image, crop_coords, crop_width, crop_height)
    image_bytes = convert_to_jpeg(pil_image)

    original_file = convert_image_to_django_uploadable(image_bytes)
    profile_thumbnail_bytes = make_profile_thumbnail(image_bytes)
    profile_thumbnail_file = convert_image_to_django_uploadable(profile_thumbnail_bytes)
    search_thumbnail_bytes = make_search_thumbnail(image_bytes)
    search_thumbnail_file = convert_image_to_django_uploadable(search_thumbnail_bytes)

    original_file.seek(0)
    profile_thumbnail_file.seek(0)
    search_thumbnail_file.seek(0)

    return original_file, profile_thumbnail_file, search_thumbnail_file


def crop_photo(pil_image, inputted_crop_coords, crop_width, crop_height):
    if not pil_image:
        return None

    # If the photo was croppped on the front end, the actual photo was not cropped but rather a shrunken down version of
    # it with the same aspect ratio. We need to convert the inputted coordinates to the coordinates on the actual photo.
    if crop_width and crop_height:
        actual_width, actual_height = pil_image.size

        # The jansy preview system should change the size of the uploaded photo by its aspect ratio to match the
        # width of the modal. Width is 100% and height is auto. So we check here if the photo increased or decreased in
        # size. It will almost always certainly be decrease in size.
        if actual_width > crop_width:
            height_ratio = actual_height / crop_height
            width_ratio = actual_width / crop_width
        else:
            height_ratio = crop_height / actual_height
            width_ratio = crop_width / actual_width

        # We round up to ensure that none of the picels the user cropped are lost.
        # The thumbnail image we ultimately create will be the right size since we resize the photo later.
        new_x = int(math.ceil(inputted_crop_coords[0] * width_ratio))
        new_y = int(math.ceil(inputted_crop_coords[1] * height_ratio))
        new_x2 = int(math.ceil(inputted_crop_coords[2] * width_ratio))
        new_y2 = int(math.ceil(inputted_crop_coords[3] * height_ratio))

        crop_coords = (new_x, new_y, new_x2, new_y2)
    else:
        new_x, new_y, new_x2, new_y2 = crop_coords = inputted_crop_coords

    cropped_image = pil_image.crop(crop_coords)
    return Image.frombytes('RGB', (new_x2 - new_x, new_y2 - new_y), cropped_image.load())


def convert_to_jpeg(pil_image):
    """
    Take an image of any format and convert it to a jpeg
    """

    if not pil_image:
        return None

    pil_image = pil_image.convert('RGB')
    image_bytes = io.BytesIO()
    pil_image.save(io.BytesIO(), 'JPEG')
    return image_bytes


def resize(image_bytes, new_width, new_height):
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
        logging.error('Could not make resize image', exc_info=True, stack_info=True)
        return None

    current_width, current_height = PIL_image.size

    # The height and width values to scale the thumbnail to
    if callable(new_width):
        new_width = new_width(current_width, current_height)

    if callable(new_height):
        new_height = new_height(current_width, current_height)

    # If the image is currently smaller than 236 pixels wide, we need to call Image.resize to scale the image up instead
    if new_width > current_width:
        PIL_image = PIL_image.resize((new_width, new_height), Image.ANTIALIAS)
    # If the image is wider than 236 pixels already, simply scale down using Image.thumbnail
    else:
        PIL_image.thumbnail((new_width, new_height), Image.ANTIALIAS)

    thumbnail_bytes = io.BytesIO()
    PIL_image.save(thumbnail_bytes, 'JPEG')

    return thumbnail_bytes


def make_profile_thumbnail(image_bytes):
    """
    Takes an Image and scales its size such that the width is equal to PROFILE_THUMBNAIL_HEIGHT
    """

    # The height and width values to scale the thumbnail to
    new_width_function = lambda width, height: int(width * (new_height / height))
    new_height = PROFILE_THUMBNAIL_HEIGHT

    return resize(image_bytes, new_width_function, new_height)


def make_search_thumbnail(image_bytes):
    """
    Takes an Image and scales its size such that the width is equal to SEARCH_THUMBNAIL_HEIGHT
    """

    # The height and width values to scale the thumbnail to
    new_width_function = lambda width, height: int(width * (new_height / height))
    new_height = SEARCH_THUMBNAIL_HEIGHT

    return resize(image_bytes, new_width_function, new_height)


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


class PhotoManager(models.Manager):

    def create_photo(self, original_photo, crop_coords, crop_width, crop_height):
        """
        Creates a ticket record using the given input
        """

        original_file, profile_thumbnail_file, search_thumbnail_file = convert_image_string(original_photo, crop_coords,
                                                                                            crop_width, crop_height)

        photo = self.model(search_thumbnail=search_thumbnail_file,
                           profile_thumbnail=profile_thumbnail_file,
                           original_file=original_file,
                           )

        photo.save(using=self._db)

        return photo


class Photo(TimeStampedModel):
    search_thumbnail = models.ImageField(upload_to=generate_search_thumbnail_name,  # So that we can use variable in custom methods
                                         null=False,
                                         blank=False,
                                         )

    profile_thumbnail = models.ImageField(upload_to=generate_profile_thumbnail_file_name,
                                          null=False,
                                          blank=False,
                                          )

    original_file = models.ImageField(upload_to=generate_original_file_name,    # Keep the original file around in case we want to store more photo sizes later.
                                      null=False,
                                      blank=False,
                                      )

    objects = PhotoManager()

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

    def __str__(self):
        return 'Photo: {}'.format(self.user)
