import datetime
from haystack import indexes
from .models import Ticket


class NoteIndex(indexes.SearchIndex, indexes.Indexable):
    title = indexes.CharField(document=True, use_template=True)

    price = indexes.FloatField

    title =



    about



    # When does the event
    start_datetime

    # The city and
    location_raw

    location



    ticket_type



    payment_method



    is_active = mod

    author = indexes.CharField(model_attr='user')
    pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        return Ticket

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())