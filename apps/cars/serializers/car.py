from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from apps.cars.models import Car
from apps.cars.serializers.car_image import CarImageDetailSerializer


class CarBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ('pk', 'owner', 'brand', 'model', 'color', 'license_plate',
                  'number_of_seats', 'production_year', 'is_deleted',)


class CarWritableSerializer(CarBaseSerializer):
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta(CarBaseSerializer.Meta):
        pass


class CarListSerializer(CarBaseSerializer):
    images = CarImageDetailSerializer(many=True)

    class Meta(CarBaseSerializer.Meta):
        fields = CarWritableSerializer.Meta.fields + ('images',)


class CarDetailSerializer(CarListSerializer):
    owner = UserPublicSerializer()

    class Meta(CarListSerializer.Meta):
        pass


class UserWithCarsPublicSerializer(UserPublicSerializer):
    cars = CarListSerializer(many=True)

    class Meta(UserPublicSerializer.Meta):
        fields = UserPublicSerializer.Meta.fields + ('cars',)
