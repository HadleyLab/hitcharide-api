from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.exceptions import ValidationError

from apps.accounts.serializers import UserPublicSerializer
from apps.cars.serializers import CarDetailSerializer
from apps.places.serializers import CityWithStateSerializer, PlaceSerializer
from apps.reviews.models import Review, ReviewAuthorType
from .models import Ride, RideStop, RideBooking, RideRequest, RideComplaint, \
    RideBookingStatus, RideStatus


class RideStopDetailSerializer(serializers.ModelSerializer):
    city = CityWithStateSerializer()
    place = PlaceSerializer()

    class Meta:
        model = RideStop
        fields = ('pk', 'city', 'place', 'order')


class RideStopWritableSerializer(serializers.ModelSerializer):

    class Meta:
        model = RideStop
        fields = ('pk', 'city', 'place', 'order')


class RidePassengerSerializer(serializers.ModelSerializer):
    passenger_display_name = serializers.SerializerMethodField()
    client = UserPublicSerializer()

    def get_passenger_display_name(self, booking):
        user = self.context['request'].user
        driver = booking.ride.car.owner
        passenger = booking.client
        has_payed_booking = booking.ride.payed_bookings.filter(
            client=user.pk).exists()

        if user == driver and booking.status == RideBookingStatus.PAYED:
            return passenger.get_full_name()

        if user == passenger or has_payed_booking:
            return passenger.get_full_name()

        return passenger.get_public_name()

    class Meta:
        model = RideBooking
        fields = ('pk', 'client', 'seats_count', 'status', 'paypal_payment_id',
                  'paypal_approval_link', 'created', 'passenger_display_name', )


class RideDetailSerializer(WritableNestedModelSerializer):
    driver_display_name = serializers.SerializerMethodField()
    car = CarDetailSerializer()
    stops = RideStopDetailSerializer(many=True)
    city_from = CityWithStateSerializer()
    place_from = PlaceSerializer()
    city_to = CityWithStateSerializer()
    place_to = PlaceSerializer()
    bookings = RidePassengerSerializer(
        source='actual_bookings', many=True)
    has_my_reviews = serializers.SerializerMethodField()
    rating = serializers.JSONField(
        read_only=True,
        source='get_rating')
    price_with_fee = serializers.DecimalField(decimal_places=2, max_digits=10)

    def get_driver_display_name(self, ride):
        user = self.context['request'].user
        driver = ride.car.owner
        has_payed_booking = ride.payed_bookings.filter(client=user.pk).exists()
        if driver == user or has_payed_booking:
            return driver.get_full_name()

        return driver.get_public_name()

    def get_has_my_reviews(self, ride):
        if ride.status != RideStatus.COMPLETED:
            return False

        user = self.context['request'].user
        ride_passengers_pks = ride.payed_bookings.values_list(
            'client_id', flat=True)
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

        return False

    class Meta:
        model = Ride
        fields = ('pk', 'stops', 'car', 'bookings', 'city_from', 'place_from',
                  'city_to', 'place_to', 'date_time', 'price', 'price_with_fee',
                  'number_of_seats', 'available_number_of_seats', 'description',
                  'status', 'has_my_reviews', 'rating', 'driver_display_name',)


class RideWritableSerializer(WritableNestedModelSerializer):
    stops = RideStopWritableSerializer(many=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.phone or not user.first_name or not user.last_name or \
                not user.is_phone_validated:
            raise ValidationError('You need to fill profile and validate '
                                  'the phone to create a ride')

        car = attrs['car']
        number_of_seats = attrs['number_of_seats']
        if number_of_seats > car.number_of_seats:
            raise ValidationError({
                'number_of_seats': 'Ensure this value is less than max number '
                                   'of seats in the car ({0}).'.format(
                    car.number_of_seats)
            })

        city_from = attrs['city_from']
        city_to = attrs['city_to']
        if city_to == city_from:
            raise ValidationError({
                'city_to': 'Choose another city which is not equal '
                           'the `from` city'
            })

        return super(RideWritableSerializer, self).validate(attrs)

    class Meta:
        model = Ride
        fields = ('pk', 'stops', 'car', 'city_from', 'place_from', 'city_to',
                  'place_to',  'date_time', 'price', 'number_of_seats',
                  'description')


class RideCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = ('cancel_reason',)


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
                  'paypal_approval_link', 'has_my_reviews', 'rating', )


class RideBookingWritableSerializer(serializers.ModelSerializer):
    client = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    ride = serializers.PrimaryKeyRelatedField(
        queryset=Ride.objects.filter(status=RideBookingStatus.CREATED))

    class Meta:
        model = RideBooking
        fields = ('pk', 'client', 'ride', 'seats_count',
                  'paypal_approval_link')
        extra_kwargs = {'paypal_approval_link': {'read_only': True}}


class RideBookingCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideBooking
        fields = ('cancel_reason',)


class RideRequestDetailSerializer(serializers.ModelSerializer):
    city_from = CityWithStateSerializer()
    place_from = PlaceSerializer()
    city_to = CityWithStateSerializer()
    place_to = PlaceSerializer()

    class Meta:
        model = RideRequest
        fields = ('pk', 'author', 'city_from', 'place_from', 'city_to',
                  'place_to', 'is_expired', 'date_time')


class RideRequestWritableSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = RideRequest
        fields = ('pk', 'author', 'city_from', 'place_from', 'city_to',
                  'place_to', 'date_time')


class RideComplaintWritableSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = RideComplaint
        fields = ('pk', 'user', 'ride', 'description')
