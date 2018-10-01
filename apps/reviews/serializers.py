from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    # author = UserSerializer() TODO: don't need to show all contact info

    class Meta:
        model = Review
        fields = ('pk', 'author', 'ride', 'subject',
                  'type', 'rating', 'comment')


class ReviewCreateSerializer(ReviewSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    class Meta(ReviewSerializer.Meta):
        pass
