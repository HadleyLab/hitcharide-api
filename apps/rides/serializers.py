from rest_framework import serializers
from drf_writable_nested import NestedCreateMixin

from api.serializers import GetOrCreateMixin
from .models import Car, Ride, RidePoint, RideBooking, RideRequest


class CarSerializer(GetOrCreateMixin):

    def create(self, validated_data):
        if 'pk' not in validated_data:
            validated_data['owner'] = self.context['request'].user

        return super(CarSerializer, self).create(validated_data)

    class Meta:
        model = Car
        fields = ('pk', 'brand', 'model', 'number_of_sits', 'photo')


class RideSerializer(NestedCreateMixin):

    car = CarSerializer()

    def create(self, validated_data):
        result = super(RideSerializer, self).create(validated_data)
        self._update_many_to_many(result, self.initial_data)
        return result

    def update(self, instance, validated_data):
        result = super(RideSerializer, self).update(instance, validated_data)
        self._update_many_to_many(instance, self.initial_data)
        return result

    def _update_many_to_many(self, ride, data):
        RidePoint.objects.filter(ride=ride).delete()
        for stop in data.get('stops', []):
            RidePoint.objects.create(
                ride=ride,
                stop_id=stop['stop'],
                cost_per_sit=stop['cost_per_sit'],
                order=stop['order'])

    class Meta:
        model = Ride
        fields = ('pk', 'stops', 'start', 'end',
                  'car', 'number_of_sits', 'description')


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

    def create(self, validated_data):
        if 'pk' not in validated_data:
            validated_data['author'] = self.context['request'].user

        return super(RideRequestSerializer, self).create(validated_data)

    class Meta:
        model = RideRequest
        fields = ('pk', 'city_from', 'city_to', 'start')
