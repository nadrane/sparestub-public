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

    def create_customer(self, user, token, card_id):
        """
        Creates a customer record using the id returned from the Stripe API
        None of the actual customer information is stored on our system, just an ID that Stripe associates with our
        customer data. This ID can be used to retrieve the customer information from Stripe's servers.
        """

        # This create a card object on the Stripe side
        stripe_customer_object = stripe.Customer.create(card=token)

        customer = self.model(stripe_id=stripe_customer_object.id,
                              customer=user
                              )
        customer.save()

        fingerprint = get_fingerprint(retrieve_token(token))

        # Make sure that the same user didn't make two accounts and use the same credit card.
        # We will create a customer object for the user but still use the old Card record.
        card = Card.get_card_from_id(fingerprint)
        if not card:
            card = Card.objects.create_card(card_id, fingerprint, customer)

        logging.info('Customer created: {}'.format(repr(customer)))

        return customer, card


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

    objects = CustomerManager()

    def __repr__(self):
        return '\n{class_object} - {id} \n' \
               'customer: {customer}'\
               .format(class_object=self.__class__,
                       id=self.stripe_id,
                       customer=repr(self.customer))

    def __str__(self):
        return str(self.customer)

    @staticmethod
    def get_customer_from_stripe(stripe_id):
        """
        We do not store any actual customer information on our system, just an ID that we can use to retrieve the
        customer information from Stripe. Do that here.
        """

        return stripe.Customer.retrieve(stripe_id)

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
    def get_customer_from_id(stripe_id):
        try:
            return Customer.objects.get(pk=stripe_id)
        except Customer.DoesNotExist:
            return None

    @staticmethod
    def customer_exists(user):
        """
        Check to see if a customer record exists in the system for a particular user.
        """

        return Customer.objects.filter(customer=user).exists()

    def charge(self, amount, card):
        """
        Bill this customer record the amount inputted. Amount should be in cents.
        Bill this using the specified card if one is supplied
        """
        try:
            stripe.Charge.create(amount=amount, # amount in cents, again
                                 currency="usd",
                                 customer=self.stripe_id,
                                 card=card.card_id,
                                 description="charging {} $5.00 for ticket match".format(self.stripe_id)
                                 )
            logging.info('Charging {} {} cents for ticket match using {}'.format(self, amount, card))

        except stripe.CardError as e:
            logging.critical('Card {} was declined for customer {} for {} cents'
                             .format(card, self, amount))
            raise StripeError
        except stripe.InvalidRequestError as e:
            logging.critical('Card {} was error out for customer {} for {} cents'
                             .format(card, self, amount))
            raise StripeError


class CardManager(models.Manager):

    def create_card(self, card_id, fingerprint, customer, create_card_on_stripe=False, token=None):
        """
        Creates a card record using the id returned from the Stripe API
        None of the actual credit card information is stored on our system, just an ID that Stripe associates with our
        card data. This ID can be used to retrieve the credit card information from Stripe's servers.
        It also allows us to specify which customer credit card we are going to charge.

        create_card_on_stripe will be called when we make a new card without making a new customer.
        We need to tell Stripe to associate the new card with their customer record.
        """

        if create_card_on_stripe:
            if not token:
                logging.error('Card creation failed. Token id absent. Failed to create card for {} with card_id {}'
                              .format(repr(customer), card_id))
                return None
            try:
                stripe_customer_object = Customer.get_customer_from_stripe(customer.stripe_id)
                stripe_customer_object.cards.create(card=token)
            except stripe.error.StripeError as e:
                logging.error('Card creation failed. Stripe error {}. Failed to create card for {} with card_id {}'
                              .format(e, repr(customer), card_id))
                return None

        card = self.model(card_id=card_id,
                          fingerprint=fingerprint,
                          customer=customer
                          )

        card.save()

        logging.info('Card created: {}'.format(repr(card)))

        return card


class Card(models.Model):
    #This ID is unique for any card that I create.
    # Use the card_id as the primary key in case a user creates
    # two accounts and tries to use the same credit card for both.
    card_id = models.CharField(primary_key=True,
                               max_length=255,   # Let's just be safe with the potential length of Stripe ids.
                               unique=True,
                               )

    # The fingerprint will be the same for any credit card of the same number with my API key
    fingerprint = models.CharField(max_length=255,)   # Let's just be safe with the potential length of Stripe ids.


    customer = models.ForeignKey(Customer,
                                 blank=False,
                                 null=False
                                 )

    objects = CardManager()

    def __repr__(self):
        return '\n{class_object} - {id} \n' \
               'customer: {customer}'\
               .format(class_object=self.__class__,
                       id=self.fingerprint,
                       customer=repr(self.customer))

    @staticmethod
    def card_exists(card_id):
        """
        Check to see if a card record exists in the system.
        This will be called before creating a new card. There will be many instances where the same user enters the
        same card twice. We need to prevent making duplicate card records.
        But there will be instances where the same user enters the same card on two different accounts. In this case,
        the fingerprints will be the same but the card_ids will not. Create a new card in this case.
        """

        return Card.objects.filter(card_id=card_id).exists()

    @staticmethod
    def get_card_from_id(card_id):
        """
        Return a card record using the id stripe gave us.
        """
        try:
            return Card.objects.get(pk=card_id)
        except Card.DoesNotExist:
            return None

    @staticmethod
    def get_card_from_fingerprint(fingerprint, customer):
        """
        Check to see if this particular customer record has used this card before.
        This should not stop another user with the same card from creating a card record.
        """
        card = Card.objects.filter(customer=customer, fingerprint=fingerprint)
        if card:
            return card[0]
        return None


class StripeError(Exception):
    """
    A generic error that we can raise when Stripe fails and then catch in the view.
    """
    pass


def retrieve_token(token_string):
    return stripe.Token.retrieve(token_string)


def get_fingerprint(token_object):
    return token_object['card']['fingerprint']


def create_customer_and_card(user, token, card_id):
    # Create a customer record to store the credit card information in the Stripe system.
    # We can use this information to charge the customer later.
    try:
        # Check to see if a customer record exists for this user.
        customer = Customer.get_customer_from_user(user)
        if customer:
            # See if this particular customer has used this particular card before.
            # Don't make a second card record if they have
            fingerprint = get_fingerprint(retrieve_token(token))
            card = Card.get_card_from_fingerprint(fingerprint, customer)
            if not card:
                card = Card.objects.create_card(card_id, fingerprint, customer, True, token)
        else:
            customer, card = Customer.objects.create_customer(user=user, token=token, card_id=card_id)
    except stripe.CardError as e:
        logging.error('Customer or card creation failed because of an invalid card. \n'
                      'user: {}\n'
                      'token: {}\n'
                      'card_id: {}\n'.format(user, token, card_id))
        raise StripeError()
    except stripe.error.StripeError as e:
        logging.error('Customer or card creation failed because of a Stripe error. \n'
                      'user: {}\n'
                      'token: {}\n'
                      'card_id: {}\n'.format(user, token, card_id))
        raise StripeError()
    return customer, card