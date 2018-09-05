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
    from_city = serializers.PrimaryKeyRelatedField(
        source='first_stop.city.pk',
        read_only=True)
    to_city = serializers.PrimaryKeyRelatedField(
        source='last_stop.city.pk',
        read_only=True
    )
    available_number_of_sits = serializers.SerializerMethodField()

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.phone or not user.first_name or not user.last_name or \
                not user.is_phone_validated:
            raise ValidationError('You need to fill profile and validate '
                                  'the phone to create a ride')

        return super(RideSerializer, self).validate(attrs)

    def get_available_number_of_sits(self, obj):
        return obj.available_number_of_sits()


    class Meta:
        model = Ride
        fields = ('pk', 'stops', 'car', 'from_city', 'to_city',
                  'available_number_of_sits', 'description')


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
