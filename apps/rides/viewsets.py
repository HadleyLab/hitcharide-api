from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from constance import config
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from apps.main.utils import send_mail, send_sms
from apps.rides.permissions import \
    RideRequestDriverPhonePermission, \
    RideBookingRequestPassengerPhonePermission, \
    RideBookingCancelPermission, RideCancelPermission
from apps.rides.utils import \
    ride_booking_execute_payment, ride_booking_create_payment, \
    cancel_ride_by_driver, create_proxy_phone_within_ride, \
    cancel_ride_booking_by_client
from .filters import RidesListFilter, MyRidesFilter, RequestsListFilter, \
    BookingsListFilter
from .mixins import ListFactoryMixin
from .models import Ride, RideBooking, RideRequest, RideComplaint, \
    RideBookingStatus, RideStatus
from .serializers import RideBookingDetailSerializer, \
    RideWritableSerializer, RideDetailSerializer, \
    RideRequestWritableSerializer, RideRequestDetailSerializer, \
    RideBookingWritableSerializer, RideComplaintWritableSerializer, \
    RideCancelSerializer, RideBookingCancelSerializer


class RideViewSet(ListFactoryMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin):
    queryset = Ride.objects.all()
    serializer_class = RideDetailSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination
    filter_backends = (RidesListFilter,)

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return RideWritableSerializer
        return self.serializer_class

    def get_permissions(self):
        # TODO: check is_phone_validated for create
        if self.action == 'list':
            return [AllowAny()]
        else:
            return super(RideViewSet, self).get_permissions()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(
            date_time__gt=timezone.now(),
            status=RideStatus.CREATED).order_by('date_time')
        return self.list_factory(queryset)(request, *args, **kwargs)

    @action(methods=['GET'], detail=False,
            filter_backends=(MyRidesFilter, RidesListFilter))
    def my(self, request, *args, **kwargs):
        queryset = Ride.order_by_future(self.get_queryset()).filter(
            car__owner=self.request.user,
            status__in=[RideStatus.CREATED,
                        RideStatus.COMPLETED,
                        RideStatus.OBSOLETE])
        return self.list_factory(queryset)(request, *args, **kwargs)

    @action(methods=['GET'], detail=False,
            filter_backends=(MyRidesFilter, RidesListFilter))
    def booked(self, request, *args, **kwargs):
        queryset = Ride.order_by_future(self.get_queryset()).filter(
            bookings__client=self.request.user
        ).distinct()
        return self.list_factory(queryset)(request, *args, **kwargs)

    @action(methods=['POST'], detail=True,
            serializer_class=RideCancelSerializer,
            permission_classes=(RideCancelPermission, ))
    def cancel(self, request, *args, **kwargs):
        ride = self.get_object()
        cancel_ride_by_driver(ride)
        serializer = self.get_serializer(ride, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'success'})

    @action(methods=['POST'], detail=True,
            permission_classes=(RideRequestDriverPhonePermission,))
    def request_driver_phone(self, request, *args, **kwargs):
        ride = self.get_object()
        proxy_phone = create_proxy_phone_within_ride(
            request.user, ride.car.owner, ride)
        return Response({'proxy_phone': proxy_phone})

    # It is wrapped with transaction.atomic to rollback
    # on nested serializer error
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super(RideViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        super(RideViewSet, self).perform_create(serializer)
        instance = serializer.instance
        requests = instance.get_ride_requests()
        for request in requests:
            send_mail('email_passenger_ride_request_ride_suggest',
                      [request.author.email],
                      {'ride': instance,
                       'ride_request': request,
                       'ride_detail': settings.RIDE_DETAIL_URL.format(
                           ride_pk=instance.pk)})
            if request.author.sms_notifications:
                send_sms('sms_passenger_ride_request_ride_suggest',
                         [request.author.normalized_phone],
                         {'ride': instance,
                          'ride_request': request,
                          'ride_detail': settings.RIDE_DETAIL_URL.format(
                              ride_pk=instance.pk)})


class RideBookingViewSet(ListFactoryMixin,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    queryset = RideBooking.objects.all()
    serializer_class = RideBookingDetailSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (BookingsListFilter,)

    def get_permissions(self):
        # TODO: check is_phone_validated for create
        return super(RideBookingViewSet, self).get_permissions()

    def get_serializer_class(self):
        if self.action in ['create']:
            return RideBookingWritableSerializer
        return self.serializer_class

    def get_queryset(self):
        return super(RideBookingViewSet, self).get_queryset().filter(
            status__in=RideBookingStatus.ACTUAL)

    @transaction.atomic
    def perform_create(self, serializer):
        ride_booking = serializer.save()

        ride_booking_create_payment(ride_booking, self.request)
        serializer.data['paypal_approval_link'] = \
            ride_booking.paypal_approval_link

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(client=request.user)
        return self.list_factory(queryset)(request, *args, **kwargs)

    @action(methods=['POST'], detail=True,
            permission_classes=(RideBookingCancelPermission,),
            serializer_class=RideBookingCancelSerializer)
    def cancel(self, request, *args, **kwargs):
        ride_booking = self.get_object()
        cancel_ride_booking_by_client(ride_booking)
        serializer = self.get_serializer(
            ride_booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'success'})

    @action(methods=['POST'], detail=True,
            permission_classes=(RideBookingRequestPassengerPhonePermission, ))
    def request_passenger_phone(self, request, *args, **kwargs):
        booking = self.get_object()
        proxy_phone = create_proxy_phone_within_ride(
            request.user, booking.client, booking.ride)
        return Response({'proxy_phone': proxy_phone})

    # This view is accessible by client without token
    @action(methods=['GET'], detail=True, permission_classes=())
    def paypal_payment_execute(self, request, *args, **kwargs):
        payer_id = request.GET.get('PayerID')
        booking = self.get_object()
        ride_detail_url = settings.RIDE_DETAIL_URL.format(
            ride_pk=booking.ride.pk)
        # TODO: catch exception instead of if
        if ride_booking_execute_payment(payer_id, booking):
            success_url = '{0}?execution=success'.format(
                ride_detail_url)
            return HttpResponseRedirect(success_url)

        fail_url = '{0}?execution=fail'.format(ride_detail_url)
        return HttpResponseRedirect(fail_url)


class RideRequestViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    queryset = RideRequest.objects.all().order_by('date_time')
    serializer_class = RideRequestDetailSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (RequestsListFilter, )

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        else:
            return super(RideRequestViewSet, self).get_permissions()

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
            send_mail('email_manager_ride_complaint_created',
                      [config.MANAGER_EMAIL],
                      {'complaint': instance,
                       'ride_detail': settings.RIDE_DETAIL_URL.format(
                           ride_pk=instance.ride.pk)})
