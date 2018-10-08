from rest_framework import serializers

from .models import FlatPage


class FlatPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = FlatPage
        fields = ('slug', 'content')
