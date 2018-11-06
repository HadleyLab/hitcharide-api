from celery import shared_task
from constance import config
from django.db import transaction
from django.utils import timezone

from apps.rides.models import Ride, RideBooking, RideBookingStatus, RideStatus
from apps.rides.utils import ride_payout, send_ride_need_review


@shared_task()
@transaction.atomic
def complete_rides():
    ride_end_datetime = timezone.now() - timezone.timedelta(
        hours=config.RIDE_END_TIMEDELTA)
    finished_rides = Ride.objects.filter(
        status=RideStatus.CREATED,
        date_time__lte=ride_end_datetime,
        complaints__isnull=True)
    for ride in finished_rides.all():
        if ride.payed_bookings.exists():
            ride_payout(ride)
            send_ride_need_review(ride)
            ride.status = RideStatus.COMPLETED
        else:
            ride.status = RideStatus.OBSOLETE

        ride.save()


@shared_task()
def check_expired_time_of_ride_bookings():
    expired_datetime = timezone.now() - timezone.timedelta(minutes=15)
    RideBooking.objects.filter(
        status=RideBookingStatus.CREATED,
        created__lte=expired_datetime
    ).update(status=RideBookingStatus.CANCELED)
