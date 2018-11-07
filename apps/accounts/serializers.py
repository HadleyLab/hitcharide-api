from rest_framework import serializers

from .models import User


class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'timezone',)


class UserPublicSerializer(UserBaseSerializer):
    display_name = serializers.CharField(source='get_public_name')
    rating = serializers.JSONField(
        read_only=True,
        source='get_rating')
    rides_statistics = serializers.JSONField(
        read_only=True,
        source='get_rides_statistics')

    class Meta(UserBaseSerializer.Meta):
        fields = (
            'pk', 'display_name', 'nickname', 'age', 'photo', 'short_desc',
            'is_phone_validated', 'rating', 'rides_statistics', 'timezone',
        )


class UserDetailSerializer(UserPublicSerializer):
    display_name = serializers.CharField(source='get_full_name')

    class Meta(UserPublicSerializer.Meta):
        fields = (
            'pk', 'email', 'phone', 'display_name', 'first_name', 'last_name',
            'nickname', 'age', 'photo', 'short_desc', 'is_phone_validated',
            'paypal_account', 'rating', 'rides_statistics', 'timezone',
            'sms_notifications'
        )


class UserCreateSerializer(UserBaseSerializer):
    def create(self, validated_data):
        password = validated_data.pop('password')

        user = super(UserCreateSerializer, self).create(validated_data)
        user.is_active = False
        user.set_password(password)
        user.save()

        return user

    class Meta(UserBaseSerializer.Meta):
        fields = ('pk', 'email', 'password', 'timezone',)
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
        }


class UserUpdateSerializer(UserBaseSerializer):
    phone = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def validate(self, attrs):
        if not self.instance.is_phone_validated:
            attrs['sms_notifications'] = False

        return attrs

    class Meta(UserBaseSerializer.Meta):
        fields = (
            'pk', 'phone', 'first_name', 'last_name', 'nickname',
            'photo', 'short_desc', 'paypal_account', 'timezone',
            'sms_notifications'
        )
