from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'pk', 'email', 'phone', 'first_name', 'last_name',
            'age', 'photo', 'short_desc'
        )
