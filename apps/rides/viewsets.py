from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from dbmail import send_db_mail
from constance import config
from rest_framework.pagination import LimitOffsetPagination

from config.pagination import DefaultPageNumberPagination
from .filters import RidesListFilter, MyRidesFilter
from .mixins import ListFactoryMixin
from .models import Car, Ride, RideBooking, RideRequest, RideComplaint
from .serializers import CarSerializer, RideBookingDetailSerializer, \
    RideWritableSerializer, RideDetailSerializer, \
    RideRequestWritableSerializer, RideRequestDetailSerializer, \
    RideBookingWritableSerializer, RideComplaintWritableSerializer


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
    queryset = Ride.objects.all().order_by('date_time')
    serializer_class = RideDetailSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = DefaultPageNumberPagination
    filter_backends = (RidesListFilter,)

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return RideWritableSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = super(RideViewSet, self).get_queryset()

        if self.action in ['my', 'update', 'destroy']:
            queryset = queryset.filter(car__owner=self.request.user)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(
            date_time__gt=timezone.now())
        return self.list_factory(queryset)(request, *args, **kwargs)

    @action(methods=['GET'], detail=False,
            filter_backends=(MyRidesFilter, RidesListFilter))
    def my(self, request, *args, **kwargs):
        return self.list_factory(self.get_queryset())(request, *args, **kwargs)

    @action(methods=['GET'], detail=False,
            filter_backends=(MyRidesFilter, RidesListFilter))
    def booked(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(
            bookings__client=request.user
        ).distinct()
        return self.list_factory(queryset)(request, *args, **kwargs)

    # Wrap with transaction.atomic to rollback on nested serializer error
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(RideViewSet, self).create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super(RideViewSet, self).update(request, *args, **kwargs)

    def perform_update(self, serializer):
        super(RideViewSet, self).perform_update(serializer)
        instance = serializer.instance
        if instance.get_booked_seats_count():
            send_db_mail('ride_has_been_edited',
                         instance.get_clients_emails(),
                         {'ride': instance})

    def perform_destroy(self, instance):
        if instance.get_booked_seats_count():
            send_db_mail('ride_has_been_deleted',
                         instance.get_clients_emails(),
                         {'ride': instance})
        return super(RideViewSet, self).perform_destroy(instance)


class RideListViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Ride.objects.all().order_by('date_time')
    serializer_class = RideDetailSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (RidesListFilter,)


class RideBookingViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    queryset = RideBooking.objects.all()
    serializer_class = RideBookingDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['create']:
            return RideBookingWritableSerializer
        return self.serializer_class

    def get_queryset(self):
        return super(RideBookingViewSet, self).get_queryset().filter(
            client=self.request.user)


class RideRequestViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    queryset = RideRequest.objects.all().order_by('created')
    serializer_class = RideRequestDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return RideRequestWritableSerializer
        return self.serializer_class

    def get_queryset(self):
        result = super(RideRequestViewSet, self).get_queryset()

        if self.action in ['create', 'update', 'destroy', 'my']:
            result = result.filter(author=self.request.user)
        elif self.action == 'list':
            result = result.filter(date_time__gt=timezone.now())

        return result

    @action(methods=['GET'], detail=False)
    def my(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RideComplaintViewSet(mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = RideComplaintWritableSerializer
    queryset = RideComplaint.objects.all().order_by('date_time')
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        super(RideComplaintViewSet, self).perform_create(serializer)
        instance = serializer.instance
        if config.MANAGER_EMAIL:
            send_db_mail('new_ride_complaint',
                         [config.MANAGER_EMAIL],
                         {'complaint': instance})
