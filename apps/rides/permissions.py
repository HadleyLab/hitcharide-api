from rest_framework.permissions import IsAuthenticated, BasePermission

from apps.rides.models import RideBookingStatus, RideStatus


class IsRideOwner(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.car.owner == request.user


class IsRideBookingClient(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.client == request.user


class IsRideBookingActual(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.status in RideBookingStatus.ACTUAL


class RequestDriverPhonePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        has_payed_booking = request.user.pk in obj.payed_bookings.values_list(
            'client', flat=True)
        is_ride_actual = obj.status == RideStatus.CREATED
        return has_payed_booking and is_ride_actual


class RequestPassengerPhonePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        is_ride_driver = obj.ride.car.owner == request.user
        is_ride_actual = obj.ride.status == RideStatus.CREATED
        return is_ride_driver and is_ride_actual
