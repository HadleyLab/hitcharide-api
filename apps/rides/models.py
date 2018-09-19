from django.db import models
from django.utils import timezone

from apps.accounts.models import User
from .mixins import CreatedUpdatedMixin


class Car(models.Model):
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='cars')
    brand = models.CharField(
        max_length=50)
    model = models.CharField(
        max_length=50)
    number_of_seats = models.PositiveSmallIntegerField(
        verbose_name='Maximum number of seats in this car')
    photo = models.ImageField(
        upload_to='car_photos',
        blank=True, null=True)
    color = models.CharField(
        max_length=50)
    license_plate = models.CharField(
        max_length=50)

    def __str__(self):
        return '{0} {1} - {2}'.format(
            self.brand,
            self.model,
            self.owner.get_full_name())


class Ride(CreatedUpdatedMixin):
    car = models.ForeignKey(
        'Car',
        on_delete=models.PROTECT,
        related_name='rides')
    number_of_seats = models.PositiveSmallIntegerField(
        verbose_name='Available number of seats during ride')
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
        max_digits=10
    )

    @property
    def available_number_of_seats(self):
        return self.number_of_seats - self.get_booked_seats_count()

    def get_booked_seats_count(self):
        return sum(self.bookings.values_list('seats_count', flat=True))

    def get_clients_emails(self):
        return [item.client.email for item in self.bookings.all()]

    def __str__(self):
        return '{0} --> {1} on {2}'.format(
            self.city_from,
            self.city_to,
            self.car)


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
    CANCELED = 'canceled'
    SUCCEED = 'succeed'
    FAILED = 'failed'

    CHOICES = tuple(
        (item, item.title()) for item in [
            CREATED, PAYED, CANCELED, SUCCEED, FAILED
        ]
    )


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
        default=1
    )


    def __str__(self):
        return '{0} on {1} ({2})'.format(
            self.client,
            self.ride,
            self.get_status_display())

    class Meta:
        unique_together = ('ride', 'client')


class RideRequest(CreatedUpdatedMixin):
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


class RideComplaint(CreatedUpdatedMixin):
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
