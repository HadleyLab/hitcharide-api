from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from constance import config

from apps.rides.models import RideBookingStatus, RideStatus


class RideBookingCancelPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        is_client = obj.client == request.user
        is_ride_actual = obj.ride.status == RideStatus.CREATED

        if obj.status == RideBookingStatus.PAYED:
            delta_in_hours = \
                (obj.ride.date_time - timezone.now()) .total_seconds() / 3600
            can_be_canceled = \
                delta_in_hours > config.RIDE_BOOKING_CANCEL_END_TIMEDELTA
            return is_client and is_ride_actual and can_be_canceled

        if obj.status == RideBookingStatus.CREATED:
            return is_client and is_ride_actual

        return False


class RideCancelPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        is_ride_driver = obj.car.owner == request.user
        is_ride_actual = obj.status == RideStatus.CREATED
        return is_ride_driver and is_ride_actual


class RideRequestDriverPhonePermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        has_payed_booking = request.user.pk in obj.payed_bookings.values_list(
            'client', flat=True)
        is_ride_actual = obj.status == RideStatus.CREATED
        return has_payed_booking and is_ride_actual


class RideBookingRequestPassengerPhonePermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        is_ride_driver = obj.ride.car.owner == request.user
        is_ride_actual = obj.ride.status == RideStatus.CREATED
        is_ride_booking_actual = obj.status in RideBookingStatus.ACTUAL
        return is_ride_driver and is_ride_actual and is_ride_booking_actual
