from rest_framework import serializers

from apps.cars.models import CarImage


class CarImageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ('pk', 'image')


class CarImageWritableSerializer(CarImageDetailSerializer):
    class Meta(CarImageDetailSerializer.Meta):
        pass
