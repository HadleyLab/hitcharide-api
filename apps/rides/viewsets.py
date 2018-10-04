from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from constance import config
from rest_framework.pagination import LimitOffsetPagination

from apps.cars.serializers import CarDetailSerializer, CarWritableSerializer
from apps.main.utils import send_mail
from apps.rides.utils import ride_booking_refund, \
    ride_booking_execute_payment, ride_booking_create_payment, \
    cancel_ride_by_driver
from .filters import RidesListFilter, MyRidesFilter, RequestsListFilter, \
    BookingsListFilter
from .mixins import ListFactoryMixin
from .models import Ride, RideBooking, RideRequest, RideComplaint, \
    RideBookingStatus
from apps.cars.models import Car
from .serializers import RideBookingDetailSerializer, \
    RideWritableSerializer, RideDetailSerializer, \
    RideRequestWritableSerializer, RideRequestDetailSerializer, \
    RideBookingWritableSerializer, RideComplaintWritableSerializer


class CarViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.DestroyModelMixin):
    queryset = Car.objects.all()
    serializer_class = CarDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return CarWritableSerializer
        return self.serializer_class

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
    pagination_class = LimitOffsetPagination
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

    @action(methods=['GET'], detail=True)
    def cancel_ride_by_driver(self, request, *args, **kwargs):
        ride = self.get_object()
        if request.user == ride.car.owner:
            if cancel_ride_by_driver(ride):
                return HttpResponse(status=200)

        return HttpResponse(status=500)

        # Wrap with transaction.atomic to rollback on nested serializer error
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(RideViewSet, self).create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super(RideViewSet, self).update(request, *args, **kwargs)

    def perform_create(self, serializer):
        super(RideViewSet, self).perform_create(serializer)
        instance = serializer.instance
        requests = instance.get_ride_requests()
        for request in requests:
            send_mail('new_ride_for_ride_request',
                      [request.author.email],
                      {'ride': instance,
                       'ride_request': request,
                       'ride_url': settings.RIDE_DETAIL_URL.format(
                           ride_pk=instance.pk)})

    def perform_update(self, serializer):
        super(RideViewSet, self).perform_update(serializer)
        instance = serializer.instance
        if instance.get_booked_seats_count():
            send_mail('ride_has_been_edited',
                      instance.get_clients_emails(),
                      {'ride': instance})

    def perform_destroy(self, instance):
        if instance.get_booked_seats_count():
            send_mail('ride_has_been_deleted',
                      instance.get_clients_emails(),
                      {'ride': instance})
        return super(RideViewSet, self).perform_destroy(instance)


class RideBookingViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    queryset = RideBooking.objects.all()
    serializer_class = RideBookingDetailSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (BookingsListFilter,)

    def get_serializer_class(self):
        if self.action in ['create']:
            return RideBookingWritableSerializer
        return self.serializer_class

    def get_queryset(self):
        return super(RideBookingViewSet, self).get_queryset().filter(
            client=self.request.user,
            status__in=RideBookingStatus.ACTUAL
        )

    @transaction.atomic
    def perform_create(self, serializer):
        ride_booking = serializer.save()

        send_mail('client_booked_a_ride',
                  [ride_booking.client.email],
                  {'ride': ride_booking.ride})
        send_mail('driver_somebody_booked_a_ride',
                  [ride_booking.ride.car.owner.email],
                  {'ride': ride_booking.ride})

        ride_booking_create_payment(ride_booking, self.request)
        serializer.data['paypal_approval_link'] = \
            ride_booking.paypal_approval_link

    @action(methods=['GET'], detail=True, permission_classes=())
    def paypal_payment_execute(self, request, pk, *args, **kwargs):
        payer_id = request.GET.get('PayerID')
        ride_booking = RideBooking.objects.get(pk=pk)
        ride_detail_url = settings.RIDE_DETAIL_URL.format(
            ride_pk=ride_booking.ride.pk)
        # TODO: catch exception instead of if
        if ride_booking_execute_payment(payer_id, ride_booking):
            success_url = '{0}?execution=success'.format(
                ride_detail_url)
            return HttpResponseRedirect(success_url)

        fail_url = '{0}?execution=fail'.format(ride_detail_url)
        return HttpResponseRedirect(fail_url)

    @action(methods=['POST'], detail=True)
    def paypal_payment_refund(self, request, *args, **kwargs):
        ride_booking = self.get_object()

        if ride_booking_refund(ride_booking):
            send_mail('client_ride_booking_refunded',
                      [ride_booking.client.email],
                      {'ride_booking': ride_booking})
            send_mail('owner_ride_booking_refunded',
                      [ride_booking.ride.owner.email],
                      {'ride_booking': ride_booking})

            return HttpResponse(status=200)

        return HttpResponse(status=500)


class RideRequestViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    queryset = RideRequest.objects.all().order_by('created')
    serializer_class = RideRequestDetailSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (RequestsListFilter, )

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
            send_mail('new_ride_complaint',
                      [config.MANAGER_EMAIL],
                      {'complaint': instance})
