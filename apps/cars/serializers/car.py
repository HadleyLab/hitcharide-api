from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer
from apps.cars.models import Car
from apps.cars.serializers.car_image import CarImageDetailSerializer


class CarWritableSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Car
        fields = ('pk', 'owner', 'brand', 'model', 'color', 'license_plate',
                  'number_of_seats', 'production_year')


class CarListSerializer(serializers.ModelSerializer):
    images = CarImageDetailSerializer(many=True)

    class Meta(CarWritableSerializer.Meta):
        fields = CarWritableSerializer.Meta.fields + ('images',)


class CarDetailSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    images = CarImageDetailSerializer(many=True)

    class Meta:
        model = Car
        fields = ('pk', 'owner', 'brand', 'model', 'color', 'license_plate',
                  'number_of_seats', 'images', 'production_year')


class UserWithCarsSerializer(UserSerializer):
    cars = CarListSerializer(many=True)

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('cars',)
