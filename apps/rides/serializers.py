from rest_framework import serializers
from drf_writable_nested import NestedCreateMixin, NestedUpdateMixin
from rest_framework.exceptions import ValidationError

from config.serializers import GetOrCreateMixin
from .models import Car, Ride, RidePoint, RideBooking, RideRequest


class CarSerializer(GetOrCreateMixin):

    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Car
        fields = ('pk', 'owner', 'brand', 'model', 'number_of_sits', 'photo')


class RidePointSerializer(GetOrCreateMixin):

    class Meta:
        model = RidePoint
        fields = ('pk', 'city', 'cost_per_sit', 'order', 'date_time')


class RideSerializer(NestedCreateMixin, NestedUpdateMixin):

    car = CarSerializer()
    stops = RidePointSerializer(many=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.phone or not user.first_name or not user.last_name:
            raise ValidationError('You need to fill profile to create a ride')

        return super(RideSerializer, self).validate(attrs)

    class Meta:
        model = Ride
        fields = ('pk', 'stops', 'car', 'number_of_sits', 'description')


class RideBookingSerializer(serializers.ModelSerializer):

    ride = RideSerializer()
    status = serializers.CharField(read_only=True)
    client = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = RideBooking
        fields = ('pk', 'client', 'ride', 'status')


class RideRequestSerializer(serializers.ModelSerializer):

    is_expired = serializers.BooleanField(read_only=True)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = RideRequest
        fields = ('pk', 'author', 'city_from', 'city_to', 'is_expired', 'start')
