from haystack import indexes
from .models import Ticket


class TicketIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    about = indexes.CharField(model_attr='about')

    start_datetime = indexes.DateTimeField(model_attr='start_datetime')

    start_date = indexes.DateField(model_attr='start_date')

    location = indexes.CharField(model_attr='location')

    ticket_type = indexes.CharField(model_attr='ticket_type')

    payment_method = indexes.CharField(model_attr='payment_method')

    is_active = indexes.CharField(model_attr='is_active')

    poster_rating = indexes.IntegerField(model_attr='rating',
                                         null=True,
                                         )

    price = indexes.IntegerField(model_attr='price')

    def get_model(self):
        return Ticket

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()