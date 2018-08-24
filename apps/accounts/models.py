from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core import validators
from django.db.models.signals import pre_save
from django.dispatch import receiver


class User(AbstractUser):
    email = models.EmailField(
        'email address',
        unique=True)
    phone = models.CharField(
        max_length=20)
    age = models.IntegerField(
        blank=True, null=True,
        validators=[
            validators.MinValueValidator(0),
            validators.MaxValueValidator(100),
        ]
    )
    photo = models.ImageField(
        upload_to='user_photos',
        blank=True, null=True)
    short_desc = models.TextField(
        blank=True, null=True)


@receiver(pre_save, sender=User)
def set_up_username(sender, instance, *args, **kwargs):
    instance.username = instance.email
