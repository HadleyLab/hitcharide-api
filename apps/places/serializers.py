from rest_framework import serializers

from .models import State, City


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = ('pk', 'name')


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('pk', 'name')


class CityWithStateSerializer(serializers.ModelSerializer):

    state = StateSerializer()

    class Meta:
        model = City
        fields = ('pk', 'name', 'state')
