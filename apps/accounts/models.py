from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core import validators


class User(AbstractUser):
    age = models.IntegerField(
        validators=[
            validators.MinValueValidator(0),
            validators.MaxValueValidator(100),
        ]
    )
    photo = models.ImageField(
        upload_to='user_photos',
        blank=True, null=True)
    phone = models.CharField(
        max_length=20)
    short_desc = models.TextField(
        blank=True, null=True)
