from decimal import Decimal

from constance import config
from django.db import models
from django.db.models import Q, Case, When, BooleanField
from django.core.validators import MinValueValidator
from django.utils import timezone

from apps.reviews.models import Review, ReviewAuthorType
from apps.reviews.utils import calc_rating
from .mixins import CreatedUpdatedMixin


class RideStatus(object):
    CREATED = 'created'
    COMPLETED = 'completed'
    CANCELED = 'canceled'

    CHOICES = tuple(
        (item, item.title()) for item in [
            CREATED, COMPLETED, CANCELED
        ]
    )


class Ride(CreatedUpdatedMixin, models.Model):
    car = models.ForeignKey(
        'cars.Car',
        on_delete=models.PROTECT,
        related_name='rides')
    number_of_seats = models.PositiveSmallIntegerField(
        verbose_name='Available number of seats during ride',
        validators=[MinValueValidator(1)]
    )
    description = models.TextField(
        blank=True, null=True)
    city_from = models.ForeignKey(
        'places.City',
        on_delete=models.PROTECT,
        related_name='+')
    city_to = models.ForeignKey(
        'places.City',
        on_delete=models.PROTECT,
        related_name='+')
    date_time = models.DateTimeField()
    price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    status = models.CharField(
        max_length=10,
        default=RideStatus.CREATED,
        choices=RideStatus.CHOICES)
    cancel_reason = models.TextField(
        blank=True,
        null=False
    )

    @property
    def available_number_of_seats(self):
        return self.number_of_seats - self.get_booked_seats_count()

    @property
    def total_for_driver(self):
        return self.get_booked_seats_count() * self.price

    @property
    def fee_price(self):
        system_fee = Decimal(config.SYSTEM_FEE)
        coef = Decimal("0.01")
        return self.price * (system_fee * coef)

    @property
    def price_with_fee(self):
        return self.price + self.fee_price

    @property
    def actual_bookings(self):
        return self.bookings.filter(
            status__in=RideBookingStatus.ACTUAL
        )

    def get_booked_seats_count(self):
        return sum(self.bookings.filter(status=RideBookingStatus.PAYED).
                   values_list('seats_count', flat=True))

    def get_clients_emails(self, status=None):
        if status:
            return [item.client.email for item in self.bookings.filter(
                status=status)]
        else:
            return [item.client.email for item in self.bookings.all()]

    def get_ride_requests(self):
        stops_cities = self.stops.values_list('city', flat=True)

        return RideRequest.objects.filter(
            Q(city_to__in=stops_cities) | Q(city_to=self.city_to),
            date_time__gte=timezone.now(),
            city_from=self.city_from,
            date_time__range=(
                self.date_time - timezone.timedelta(days=1),
                self.date_time + timezone.timedelta(days=3)))

    def get_rating(self):
        return calc_rating(self.reviews.filter(
            author_type=ReviewAuthorType.PASSENGER))

    def get_printable_title(self):
        return '{0} - {1} {2}'.format(
            self.city_from,
            self.city_to,
            self.date_time.strftime('%m/%d/%Y'))

    def __str__(self):
        return '{0} - {1} on {2} {3}'.format(
            self.city_from,
            self.city_to,
            self.car,
            self.date_time.strftime('%m/%d/%Y'))

    @staticmethod
    def order_by_future(queryset):
        return queryset.annotate(
            is_future=Case(
                When(
                    date_time__gt=timezone.now(),
                    then=True
                ),
                default=False,
                output_field=BooleanField()
            )
        ).order_by('-is_future', 'date_time')


class RideStop(models.Model):
    ride = models.ForeignKey(
        'Ride',
        on_delete=models.CASCADE,
        related_name='stops')
    city = models.ForeignKey(
        'places.City',
        on_delete=models.PROTECT)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.city


class RideBookingStatus(object):
    CREATED = 'created'
    PAYED = 'payed'
    CANCELED = 'canceled'  # Passenger cancels
    REVOKED = 'revoked'  # Driver cancels

    CHOICES = tuple(
        (item, item.title()) for item in [
            CREATED, PAYED, CANCELED, REVOKED
        ]
    )

    ACTUAL = [CREATED, PAYED]


class RideBooking(CreatedUpdatedMixin):
    ride = models.ForeignKey(
        'Ride',
        on_delete=models.CASCADE,
        related_name='bookings')
    client = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='bookings')
    status = models.CharField(
        max_length=10,
        default=RideBookingStatus.CREATED,
        choices=RideBookingStatus.CHOICES)
    seats_count = models.IntegerField(
        default=1)
    paypal_payment_id = models.TextField(
        blank=True,
        null=True)
    paypal_approval_link = models.TextField(
        blank=True,
        null=True)
    cancel_reason = models.TextField(
        blank=True,
        null=False)

    def get_rating(self):
        return calc_rating(Review.objects.filter(
            ride=self.ride,
            author_type=ReviewAuthorType.DRIVER,
            subject=self.client))

    def __str__(self):
        return '{0} on {1} ({2})'.format(
            self.client,
            self.ride,
            self.get_status_display())


class RideRequest(CreatedUpdatedMixin, models.Model):
    author = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='requests')
    city_from = models.ForeignKey(
        'places.City',
        on_delete=models.PROTECT,
        related_name='+')
    city_to = models.ForeignKey(
        'places.City',
        on_delete=models.PROTECT,
        related_name='+')
    date_time = models.DateTimeField()

    @property
    def is_expired(self):
        return self.date_time < timezone.now()

    def __str__(self):
        return '{0} to {1} {2}'.format(
            self.city_from,
            self.city_to,
            self.date_time)


class RideComplaintStatus(object):
    NEW = 'new'
    CONSIDERED = 'considered'
    CONFIRMED = 'confirmed'
    DISAPPROVED = 'disapproved'

    CHOICES = tuple(
        (item, item.title()) for item in [
            NEW, CONSIDERED, CONFIRMED, DISAPPROVED
        ]
    )


class RideComplaint(CreatedUpdatedMixin, models.Model):
    ride = models.ForeignKey(
        'Ride',
        on_delete=models.CASCADE,
        related_name='complaints')
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='complaints')
    description = models.TextField(
        blank=True, null=True)
    status = models.CharField(
        max_length=10,
        default=RideComplaintStatus.NEW,
        choices=RideComplaintStatus.CHOICES)
