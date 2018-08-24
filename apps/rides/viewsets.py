from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Car, Ride, RideBooking, RideRequest
from .serializers import CarSerializer, RideSerializer, \
    RideBookingSerializer, RideRequestSerializer


class CarViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.DestroyModelMixin):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return super(CarViewSet, self).get_queryset().filter(
            owner=self.request.user)


class RideViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super(RideViewSet, self).get_queryset()

        if self.action in ['my', 'destroy']:
            return queryset.filter(car__owner=self.request.user)
        else:
            return queryset.filter(start__gt=timezone.now())

    @action(methods=['GET'], detail=False)
    def my(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RideBookingViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.DestroyModelMixin):
    queryset = RideBooking.objects.all()
    serializer_class = RideBookingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return super(RideBookingViewSet, self).get_queryset().filter(
            client=self.request.user)


class RideRequestViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin):
    queryset = RideRequest.objects.all().order_by('created')
    serializer_class = RideRequestSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        result = super(RideRequestViewSet, self).get_queryset()

        if self.action in ['create', 'update', 'destroy', 'my']:
            result = result.filter(author=self.request.user)

        return result

    @action(methods=['GET'], detail=False)
    def my(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
