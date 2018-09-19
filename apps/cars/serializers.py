from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer
from apps.cars.models import Car


class CarSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = Car
        fields = ('pk', 'owner', 'brand', 'model', 'color', 'license_plate',
                  'number_of_seats', 'photo')


class UserWithCarsSerializer(UserSerializer):
    cars = CarSerializer(many=True)

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            'cars',
        )
