from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.rides.mixins import CreatedUpdatedMixin


class ReviewAuthorType(object):
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
        related_name='my_reviews')
    ride = models.ForeignKey(
        'rides.Ride',
        on_delete=models.PROTECT,
        related_name='reviews')
    subject = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='reviews')
    author_type = models.PositiveSmallIntegerField(
        choices=ReviewAuthorType.CHOICES)
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ])
    comment = models.TextField(
        blank=True, null=True)

    def __str__(self):
        return '{0} --> {1} ({2})'.format(
            self.author, self.subject, self.rating)

    class Meta:
        unique_together = ('ride', 'author', 'subject')
