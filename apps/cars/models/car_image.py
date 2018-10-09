from django.db import models

from apps.cars.upload_paths import car_photo_path
from apps.main.storages import public_storage
from apps.rides.mixins import CreatedUpdatedMixin


class CarImage(CreatedUpdatedMixin):
    car = models.ForeignKey(
        'cars.Car',
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to=car_photo_path,
        storage=public_storage
    )
