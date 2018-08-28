from rest_framework import serializers
from drf_writable_nested import NestedCreateMixin

from config.serializers import GetOrCreateMixin
from .models import Car, Ride, RidePoint, RideBooking, RideRequest


class CarSerializer(GetOrCreateMixin):

    def create(self, validated_data):
        if 'pk' not in validated_data:
            validated_data['owner'] = self.context['request'].user

        return super(CarSerializer, self).create(validated_data)

    class Meta:
        model = Car
        fields = ('pk', 'brand', 'model', 'number_of_sits', 'photo')


class RidePointSerializer(GetOrCreateMixin):

    class Meta:
        model = RidePoint
        fields = ('pk', 'city', 'cost_per_sit', 'order', 'date_time')


class RideSerializer(NestedCreateMixin):

    car = CarSerializer()
    stops = RidePointSerializer(many=True)

    class Meta:
        model = Ride
        fields = ('pk', 'stops', 'car', 'number_of_sits', 'description')


class RideBookingSerializer(serializers.ModelSerializer):

    ride = RideSerializer()
    status = serializers.CharField(read_only=True)

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        return super(RideBookingSerializer, self).create(validated_data)

    class Meta:
        model = RideBooking
        fields = ('pk', 'ride', 'status')


class RideRequestSerializer(serializers.ModelSerializer):

    is_expired = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        if 'pk' not in validated_data:
            validated_data['author'] = self.context['request'].user

        return super(RideRequestSerializer, self).create(validated_data)

    class Meta:
        model = RideRequest
        fields = ('pk', 'city_from', 'city_to', 'is_expired', 'start')
