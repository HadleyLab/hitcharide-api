from django.db import models
from django.utils import timezone

from denorm import denormalized, depend_on_related

from .mixins import CreatedUpdatedMixin


class Car(models.Model):
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='cars')
    brand = models.CharField(
        max_length=50)
    model = models.CharField(
        max_length=50)
    number_of_sits = models.PositiveSmallIntegerField(
        verbose_name='Maximum number of sits in this car')
    photo = models.ImageField(
        upload_to='car_photos',
        blank=True, null=True)

    def __str__(self):
        return '{0} {1} - {2}'.format(
            self.brand,
            self.model,
            self.owner.get_full_name())


class Ride(CreatedUpdatedMixin):
    car = models.ForeignKey(
        'Car',
        on_delete=models.CASCADE,
        related_name='rides')
    number_of_sits = models.PositiveSmallIntegerField(
        verbose_name='Available number of sits during ride')
    description = models.TextField(
        blank=True, null=True)

    @denormalized(models.ForeignKey, to='RidePoint', on_delete=models.SET_NULL,
                  related_name='+', blank=True, null=True)
    @depend_on_related('RidePoint', foreign_key='first_stop')
    def first_stop(self):
        return self.stops.order_by('order').first()

    @denormalized(models.ForeignKey, to='RidePoint', on_delete=models.SET_NULL,
                  related_name='+', blank=True, null=True)
    @depend_on_related('RidePoint', foreign_key='last_stop')
    def last_stop(self):
        return self.stops.order_by('order').last()

    def __str__(self):
        return '{0} --> {1} on {2}'.format(
            self.first_stop,
            self.last_stop,
            self.car)


class RidePoint(models.Model):
    ride = models.ForeignKey(
        'Ride',
        on_delete=models.CASCADE,
        related_name='stops')
    city = models.ForeignKey(
        'places.City',
        on_delete=models.CASCADE)
    cost_per_sit = models.PositiveIntegerField()
    order = models.IntegerField(default=0)
    date_time = models.DateTimeField()

    def __str__(self):
        return '{0} : {1}'.format(self.city, self.date_time)


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
        on_delete=models.CASCADE,
        related_name='bookings')
    status = models.CharField(
        max_length=10,
        default=RideBookingStatus.CREATED,
        choices=RideBookingStatus.CHOICES)

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
        on_delete=models.CASCADE,
        related_name='requests')
    city_from = models.ForeignKey(
        'places.City',
        on_delete=models.CASCADE,
        related_name='+')
    city_to = models.ForeignKey(
        'places.City',
        on_delete=models.CASCADE,
        related_name='+')
    start = models.DateTimeField()

    @property
    def is_expired(self):
        return self.start < timezone.now()
