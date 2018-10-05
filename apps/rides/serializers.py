from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.exceptions import ValidationError

from apps.accounts.serializers import UserSerializer
from apps.cars.serializers import CarDetailSerializer
from apps.places.serializers import CityWithStateSerializer
from apps.reviews.models import Review, ReviewAuthorType
from .models import Ride, RideStop, RideBooking, RideRequest, RideComplaint, \
    RideBookingStatus


class RideStopDetailSerializer(serializers.ModelSerializer):
    city = CityWithStateSerializer()

    class Meta:
        model = RideStop
        fields = ('pk', 'city', 'order')


class RideStopWritableSerializer(serializers.ModelSerializer):

    class Meta:
        model = RideStop
        fields = ('pk', 'city', 'order')


class RidePassengerSerializer(serializers.ModelSerializer):
    client = UserSerializer()

    class Meta:
        model = RideBooking
        fields = ('pk', 'client', 'seats_count', 'status', 'paypal_payment_id',
                  'paypal_approval_link', 'created',)


class RideDetailSerializer(WritableNestedModelSerializer):
    car = CarDetailSerializer()
    stops = RideStopDetailSerializer(many=True)
    city_from = CityWithStateSerializer()
    city_to = CityWithStateSerializer()
    bookings = RidePassengerSerializer(source='actual_bookings',
                                       many=True)
    has_my_reviews = serializers.SerializerMethodField()
    rating = serializers.JSONField(
        read_only=True,
        source='get_rating')

    def get_has_my_reviews(self, ride):
        user = self.context['request'].user
        ride_passengers_pks = ride.bookings.filter(
            status=RideBookingStatus.PAYED
        ).values_list('client_id', flat=True)
        ride_driver = ride.car.owner
        if ride_driver == user:
            # I am driver
            return Review.objects.filter(
                author=user,
                author_type=ReviewAuthorType.DRIVER,
                ride=ride,
                subject_id__in=ride_passengers_pks
            ).count() == len(ride_passengers_pks)
        else:
            # I am passenger
            if user.pk in ride_passengers_pks:
                return Review.objects.filter(
                    author=user,
                    author_type=ReviewAuthorType.PASSENGER,
                    ride=ride,
                    subject=ride_driver
                ).exists()
            else:
                return False

    class Meta:
        model = Ride
        fields = ('pk', 'stops', 'car', 'bookings', 'city_from', 'city_to',
                  'date_time', 'price', 'price_with_fee', 'number_of_seats',
                  'available_number_of_seats', 'description', 'status',
                  'has_my_reviews', 'rating')


class RideWritableSerializer(WritableNestedModelSerializer):
    stops = RideStopWritableSerializer(many=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.phone or not user.first_name or not user.last_name or \
                not user.is_phone_validated:
            raise ValidationError('You need to fill profile and validate '
                                  'the phone to create a ride')

        return super(RideWritableSerializer, self).validate(attrs)

    class Meta:
        model = Ride
        fields = ('pk', 'stops', 'car', 'city_from', 'city_to', 'date_time',
                  'price', 'number_of_seats', 'description')


class RideBookingDetailSerializer(serializers.ModelSerializer):
    ride = RideDetailSerializer()
    status = serializers.CharField(read_only=True)
    has_my_reviews = serializers.SerializerMethodField()
    rating = serializers.JSONField(
        read_only=True,
        source='get_rating')

    def get_has_my_reviews(self, booking):
        if booking.status == RideBookingStatus.PAYED:
            return Review.objects.filter(
                author=self.context['request'].user,
                author_type=ReviewAuthorType.PASSENGER,
                ride=booking.ride,
                subject=booking.ride.car.owner).exists()

        return False

    class Meta:
        model = RideBooking
        fields = ('pk', 'client', 'ride', 'seats_count', 'status',
                  'paypal_approval_link', 'has_my_reviews', 'rating')


class RideBookingWritableSerializer(serializers.ModelSerializer):
    client = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = RideBooking
        fields = ('pk', 'client', 'ride', 'seats_count',
                  'paypal_approval_link')
        extra_kwargs = {'paypal_approval_link': {'read_only': True}}


class RideRequestDetailSerializer(serializers.ModelSerializer):
    city_from = CityWithStateSerializer()
    city_to = CityWithStateSerializer()

    class Meta:
        model = RideRequest
        fields = ('pk', 'author', 'city_from', 'city_to', 'is_expired',
                  'date_time')


class RideRequestWritableSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = RideRequest
        fields = ('pk', 'author', 'city_from', 'city_to', 'date_time')


class RideComplaintWritableSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = RideComplaint
        fields = ('pk', 'user', 'ride', 'description')
