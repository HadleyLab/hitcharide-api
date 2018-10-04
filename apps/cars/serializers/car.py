from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer
from apps.cars.models import Car
from apps.cars.serializers.car_image import CarImageWritableSerializer, \
    CarImageDetailSerializer


class CarWritableSerializer(WritableNestedModelSerializer):
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    images = CarImageWritableSerializer(many=True)

    class Meta:
        model = Car
        fields = ('pk', 'owner', 'brand', 'model', 'color', 'license_plate',
                  'number_of_seats', 'images', 'production_year')


class CarDetailSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    images = CarImageDetailSerializer(many=True)

    class Meta:
        model = Car
        fields = ('pk', 'owner', 'brand', 'model', 'color', 'license_plate',
                  'number_of_seats', 'images', 'production_year')


class UserWithCarsSerializer(UserSerializer):
    cars = CarWritableSerializer(many=True)

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            'cars',
        )
