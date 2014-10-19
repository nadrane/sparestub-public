__author__ = 'nicholasdrane'

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    '''
    As an abstract class, this class object cannot actually be instantiated.
    Nevertheless, every model should probably inherit from this model.
    Provides self-updating last_modified and creation_timestamps
    as well as creation_date.
    '''

    last_modified = models.DateTimeField(auto_now=True,
                                         editable=False,
                                         default=timezone.now
                                         )

    creation_timestamp = models.DateTimeField(auto_now_add=True,
                                              editable=False,
                                              default=timezone.now
                                              )

    creation_date = models.DateField(auto_now_add=True,   # Set the creation date once when the object is first created
                                     editable=False,
                                     db_index=True        # There are many scheduled jobs that will only consider records within a certain time range
                                     )

    class Meta:
        abstract = True


class IntegerRangeField(models.IntegerField):
    '''
    An integer field that allows the user to specify minimum and maximum values
    '''
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value':self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)