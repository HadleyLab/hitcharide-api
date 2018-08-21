from django.db import models

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
    stops = models.ManyToManyField(
        'places.City',
        verbose_name='All points of route',
        related_name='rides',
        through='RidePoint')
    start = models.DateTimeField()
    end = models.DateTimeField()
    car = models.ForeignKey(
        'Car',
        on_delete=models.CASCADE,
        related_name='rides')
    number_of_sits = models.PositiveSmallIntegerField(
        verbose_name='Available number of sits during ride')
    description = models.TextField(
        blank=True, null=True)

    def __str__(self):
        return '{0} --> {1} on {2} at {3}'.format(
            self.stops.first(),
            self.stops.last(),
            self.car,
            self.start)


class RidePoint(models.Model):
    ride = models.ForeignKey(
        'Ride',
        on_delete=models.CASCADE,
        related_name='ride_stops')
    stop = models.ForeignKey(
        'places.City',
        on_delete=models.CASCADE)
    cost_per_sit = models.PositiveIntegerField()


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
        on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        default=RideBookingStatus.CREATED,
        choices=RideBookingStatus.CHOICES)

    def __str__(self):
        return '{0} on {1} ({2})'.format(
            self.client,
            self.ride,
            self.get_status_display())
