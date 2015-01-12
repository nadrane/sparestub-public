#3rd Party Imports
import stripe

# Django Imports
from django.db import models
from django.conf import settings

# SpareStub Imports
from utils.models import TimeStampedModel
from registration.models import User


class CustomerManager(models.Manager):

    def create_customer(self, stripe_id, user):
        """
        Creates a customer record using the id returned from the Stripe API
        None of the actual customer information is stored on our system, just an ID that Stripe associates with our
        customer data. This ID can be used to retrieve the customer information from Stripe's servers.
        """

        customer = self.model(stripe_id=stripe_id,
                              customer=user
                              )

        customer.save()


class Customer(TimeStampedModel):
    stripe_id = models.CharField(primary_key=True,
                                 max_length=255,   # Let's just be safe with the potential length of Stripe ids.
                                 unique=True,
                                 )

    customer = models.ForeignKey(User,
                                 null=False,
                                 blank=False,
                                 unique=True,
                                 )

    def get_customer(self):
        """
        We do not store any actual customer information on our system, just an ID that we can use to retrieve the
        customer information from Stripe. Do that here
        """
        stripe.api_key = settings.STRIPE_SECRET_API_KEY
        return stripe.Customer.retrieve(self.id)

    @staticmethod
    def customer_exists(user):
        """
        Check to see if a customer record exists in the system for a particular user.
        """
        stripe.api_key = settings.STRIPE_SECRET_API_KEY
        return Customer.objects.filter(customer=user).exists()

    objects = CustomerManager()

