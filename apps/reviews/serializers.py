from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.rides.models import RideBookingStatus
from .models import Review, ReviewType


class ReviewSerializer(serializers.ModelSerializer):
    # author = UserSerializer() TODO: don't need to show all contact info

    class Meta:
        model = Review
        fields = ('pk', 'author', 'author_type', 'ride',
                  'subject', 'rating', 'comment')


class ReviewCreateSerializer(ReviewSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())

    def validate(self, attrs):
        ride = attrs['ride']
        # TODO check ride status = finished!

        author = attrs['author']
        subject = attrs['subject']

        ride_passengers_pks = ride.bookings.filter(
            status=RideBookingStatus.SUCCEED
        ).values_list('client_id', flat=True)
        ride_driver = ride.car.owner

        if attrs['author_type'] == ReviewType.DRIVER:
            if author != ride_driver:
                raise ValidationError('Review author must be a driver '
                                      'if author_type = DRIVER')

            if subject.pk not in ride_passengers_pks:
                raise ValidationError('Review subject must be a passenger '
                                      'if author_type = DRIVER')
        else:
            if subject != ride_driver:
                raise ValidationError('Review subject must be a driver '
                                      'if author_type = PASSENGER')

            if author.pk not in ride_passengers_pks:
                raise ValidationError('Review author must be a passenger '
                                      'if author_type = PASSENGER')

        return super(ReviewCreateSerializer, self).validate(attrs)

    class Meta(ReviewSerializer.Meta):
        pass
