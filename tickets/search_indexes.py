import datetime
from haystack import indexes
from .models import Ticket


class TicketIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    about = indexes.CharField(model_attr='about')

    start_datetime = indexes.DateTimeField(model_attr='start_datetime')

    location = indexes.CharField(model_attr='location')

    ticket_type = indexes.CharField(model_attr='ticket_type')

    payment_method = indexes.CharField(model_attr='payment_method')

    is_active = indexes.CharField(model_attr='is_active')

    def build_form(self):
        return super(TicketIndex, self).build_form({'request': request})

    def get_model(self):
        return Ticket

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()