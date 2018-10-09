from rest_framework import serializers

from .models import FlatPage


class FlatPageListSerializer(serializers.ModelSerializer):

    class Meta:
        model = FlatPage
        fields = ('slug',)


class FlatPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = FlatPage
        fields = ('slug', 'content')
