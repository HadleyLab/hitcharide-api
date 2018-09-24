from celery import shared_task
from django.utils import timezone

from apps.rides.models import Ride, RideBooking, RideBookingStatus
from apps.rides.utils import ride_payout


@shared_task()
def create_payouts_for_rides():
    ride_end_datetime = timezone.now()-timezone.timedelta(hours=24)
    finished_rides = Ride.objects.filter(date_time__lte=ride_end_datetime)
    for ride in finished_rides.all():
        if len(ride.complaints) == 0:
            ride_payout(ride)

@shared_task()
def check_expired_time_of_ride_bookings():
    expired_datetime = timezone.now()-timezone.timedelta(minutes=15)
    RideBooking.objects.filter(
        status=RideBookingStatus.CREATED,
        update_lte=expired_datetime).update(status=RideBookingStatus.EXPIRED)
