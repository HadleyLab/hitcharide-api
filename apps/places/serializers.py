from rest_framework import serializers

from .models import State, City, Place


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = ('pk', 'name', 'short_name')


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('pk', 'name')


class CityWithStateSerializer(serializers.ModelSerializer):

    state = StateSerializer()

    class Meta:
        model = City
        fields = ('pk', 'name', 'state')


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('pk', 'name', 'short_name', 'category')
