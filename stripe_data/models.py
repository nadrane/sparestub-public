# Standard Imports
import logging

#3rd Party Imports
import stripe

# Django Imports
from django.db import models
from django.conf import settings

# SpareStub Imports
from utils.models import TimeStampedModel
from registration.models import User

stripe.api_key = settings.STRIPE_SECRET_API_KEY


class CustomerManager(models.Manager):

    def create_customer(self, user, token):
        """
        Creates a customer record using the id returned from the Stripe API
        None of the actual customer information is stored on our system, just an ID that Stripe associates with our
        customer data. This ID can be used to retrieve the customer information from Stripe's servers.
        """

        stripe_customer_object = stripe.Customer.create(card=token)

        customer = self.model(stripe_id=stripe_customer_object.id,
                              customer=user
                              )

        customer.save()

        logging.info('Customer created: {}'.format(customer))


class Customer(TimeStampedModel):
    stripe_id = models.CharField(primary_key=True,
                                 max_length=255,   # Let's just be safe with the potential length of Stripe ids.
                                 unique=True,
                                 )

    customer = models.ForeignKey(User,
                                 null=False,
                                 blank=False,
                                 unique=True,
                                 db_index=True,
                                 )

    def __repr__(self):
        return '{class_object} - {id} \n' \
               'customer: {customer}'\
               .format(class_object=self.__class__,
                       id=self.stripe_id,
                       customer=repr(self.customer))

    def __str__(self):
        return self.customer

    def get_customer(self):
        """
        We do not store any actual customer information on our system, just an ID that we can use to retrieve the
        customer information from Stripe. Do that here.
        """

        return stripe.Customer.retrieve(self.id)

    @staticmethod
    def get_customer_from_user(user):
        """
        Using a user record, get the Django custom record from our database. This record can be used to communicate with
        Stripe to charge the customer.
        """

        customer = Customer.objects.filter(customer=user)
        if customer:
            return customer[0]
        return None

    @staticmethod
    def customer_exists(user):
        """
        Check to see if a customer record exists in the system for a particular user.
        """

        return Customer.objects.filter(customer=user).exists()

    def charge(self, amount):
        """
        Bill this customer record the amount inputted. Amount should be in cents.
        """

        try:
            charge = stripe.Charge.create(amount=amount, # amount in cents, again
                                          currency="usd",
                                          customer=self.stripe_id,
                                          description="charging {} $5.00 for ticket match".format(self.stripe_id)
                                          )
            logging.info('charging {} $5.00 for ticket match'.format(self.stripe_id))

        except stripe.CardError as e:
            logging.critical('A card was declined for customer {} for {} cents'
                             .format(self.stripe_id, amount))
            raise StripeError
        except stripe.InvalidRequestError as e:
            logging.critical('A major error caused stripe to fail to process a payment of {} cents for customer {}'
                             .format(amount, self.stripe_id))
            raise StripeError

    objects = CustomerManager()


class StripeError(Exception):
    """
    A generic error that we can raise when Stripe fails and then catch in the view.
    """
    pass

