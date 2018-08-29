from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from config.pagination import DefaultPageNumberPagination
from .filters import RidesFilter
from .mixins import ListFactoryMixin
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


class RideViewSet(ListFactoryMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin):
    queryset = Ride.objects.all().order_by('first_stop__date_time')
    serializer_class = RideSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = DefaultPageNumberPagination
    filter_backends = (RidesFilter,)

    def get_queryset(self):
        queryset = super(RideViewSet, self).get_queryset()

        if self.action in ['my', 'update', 'destroy']:
            queryset = queryset.filter(car__owner=self.request.user)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(
            first_stop__date_time__gt=timezone.now())
        return self.list_factory(queryset)(request, *args, **kwargs)

    @action(methods=['GET'], detail=False)
    def my(self, request, *args, **kwargs):
        return self.list_factory(self.get_queryset())(request, *args, **kwargs)

    @action(methods=['GET'], detail=False)
    def booked(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(
            pk__in=RideBooking.objects.filter(
                client=self.request.user
            ).values_list('ride_id', flat=True))
        return self.list_factory(queryset)(request, *args, **kwargs)

    # Wrap with transaction.atomic to rollback on nested serializer error
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(RideViewSet, self).create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super(RideViewSet, self).update(request, *args, **kwargs)


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
        elif self.action == 'list':
            result = result.filter(start__gt=timezone.now())

        return result

    @action(methods=['GET'], detail=False)
    def my(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
