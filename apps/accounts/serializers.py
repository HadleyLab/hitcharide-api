from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'pk', 'email', 'phone', 'first_name', 'last_name',
            'age', 'photo', 'short_desc'
        )


class RegisterUserSerializer(UserSerializer):

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = super(RegisterUserSerializer, self).create(validated_data)
        user.is_active = False
        user.set_password(password)
        user.save()

        return user

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('password',)
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
        }
