from rest_framework.permissions import IsAuthenticated, BasePermission

from apps.rides.models import RideBookingStatus


class IsRideOwner(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.car.owner == request.user


class IsRideBookingClient(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.client == request.user


class IsRideBookingActual(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.status in RideBookingStatus.ACTUAL
