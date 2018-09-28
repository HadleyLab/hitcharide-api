from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.rides.mixins import CreatedUpdatedMixin


class ReviewType(object):
    DRIVER = 1
    PASSENGER = 2

    CHOICES = (
        (DRIVER, 'Driver'),
        (PASSENGER, 'Passenger')
    )


class Review(CreatedUpdatedMixin):
    author = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='reviews')
    ride = models.ForeignKey(
        'rides.Ride',
        on_delete=models.PROTECT,
        related_name='reviews')
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ])
    text = models.TextField(
        blank=True, null=True)

    class Meta:
        unique_together = ('ride', 'author')
