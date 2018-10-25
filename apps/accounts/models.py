import uuid

import pytz
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from apps.accounts.fields import PhoneField
from apps.accounts.upload_paths import user_photo_path
from apps.main.storages import public_storage
from apps.reviews.utils import calc_rating
from apps.rides.models import Ride, RideStatus, RideBooking, RideBookingStatus

TIMEZONES = [(name, name) for name in pytz.common_timezones]


class User(AbstractUser):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          unique=True)
    email = models.EmailField(
        'email address',
        unique=True)
    phone = PhoneField(
        blank=True, null=True)
    is_phone_validated = models.BooleanField(
        default=False)
    birthday = models.DateTimeField(
        blank=True, null=True)
    photo = models.ImageField(
        upload_to=user_photo_path,
        storage=public_storage,
        blank=True, null=True)
    short_desc = models.TextField(
        blank=True, null=True)
    paypal_account = models.CharField(
        max_length=150,
        blank=True, null=True)
    timezone = models.CharField(
        verbose_name='Time zone',
        max_length=32,
        choices=TIMEZONES,
        default=settings.TIME_ZONE
    )
    sms_notifications = models.BooleanField(
        default=False
    )

    __original_phone = None

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.__original_phone = self.phone

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.phone != self.__original_phone:
            self.is_phone_validated = False
            self.sms_notifications = False

        super(User, self).save(force_insert, force_update, *args, **kwargs)
        self.__original_phone = self.phone

    @property
    def age(self):
        if self.birthday:
            today = timezone.now()
            months_diff = (today.month, today.day) < \
                          (self.birthday.month, self.birthday.day)
            return today.year - self.birthday.year - months_diff
        else:
            return None

    @property
    def normalized_phone(self):
        if not self.is_phone_validated:
            return None

        return '+{0}'.format(self.phone)

    def get_rating(self):
        return calc_rating(self.reviews.all())

    def get_rides_statistics(self):
        completed_rides_driver = Ride.objects.filter(
            car__owner=self,
            status=RideStatus.COMPLETED).count()
        canceled_rides_driver = Ride.objects.filter(
            car__owner=self,
            status=RideStatus.CANCELED).count()

        completed_rides_passenger = RideBooking.objects.filter(
            client=self,
            ride__status=RideStatus.COMPLETED).count()
        canceled_rides_passenger = RideBooking.objects.filter(
            client=self,
            status=RideBookingStatus.CANCELED).count()

        return {
            'completed': completed_rides_driver + completed_rides_passenger,
            'canceled': canceled_rides_driver + canceled_rides_passenger
        }


@receiver(pre_save, sender=User)
def set_up_username(sender, instance, *args, **kwargs):
    instance.username = instance.email
