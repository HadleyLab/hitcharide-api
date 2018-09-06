from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.exceptions import ValidationError

from apps.places.serializers import CitySerializer
from .models import Car, Ride, RideStop, RideBooking, RideRequest


class CarSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Car
        fields = ('pk', 'owner', 'brand', 'model', 'color', 'license_plate',
                  'number_of_seats', 'photo')


class RideStopDetailSerializer(serializers.ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = RideStop
        fields = ('pk', 'city', 'order')


class RideStopWritableSerializer(serializers.ModelSerializer):

    class Meta:
        model = RideStop
        fields = ('pk', 'city', 'order')


class RideDetailSerializer(WritableNestedModelSerializer):
    car = CarSerializer()
    stops = RideStopDetailSerializer(many=True)

    class Meta:
        model = Ride
        fields = ('pk', 'stops', 'car', 'city_from', 'city_to', 'date_time',
                  'price', 'number_of_seats', 'available_number_of_seats',
                  'description')


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
    client = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = RideBooking
        fields = ('pk', 'client', 'ride', 'status')


class RideRequestDetailSerializer(serializers.ModelSerializer):
    city_from = CitySerializer()
    city_to = CitySerializer()

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
