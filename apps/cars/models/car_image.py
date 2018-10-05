from django.db import models

from apps.rides.mixins import CreatedUpdatedMixin


class CarImage(CreatedUpdatedMixin):
    car = models.ForeignKey(
        'cars.Car',
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='car_images',
    )
