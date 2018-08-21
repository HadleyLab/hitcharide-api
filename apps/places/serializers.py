from rest_framework import serializers

from .models import State, City


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('pk', 'name')


class StateSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True)

    class Meta:
        model = State
        fields = ('pk', 'name', 'cities')
