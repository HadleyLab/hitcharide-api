from rest_framework import viewsets, mixins, status, response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings

from apps.accounts.models import User
from apps.cars.serializers import UserWithCarsPublicSerializer
from apps.main.utils import twilio_create_proxy_phone


class UserDetailViewSet(mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserWithCarsPublicSerializer
    permission_classes = (IsAuthenticated,)

    @action(methods=['POST'], detail=True)
    def create_proxy_phone(self, request, *args, **kwargs):
        source_user = request.user
        destination_user = self.get_object()

        if not source_user.is_phone_validated:
            return response.Response(
                status=status.HTTP_400_BAD_REQUEST,
                data='Please specify and validate your phone number '
                     'in the profile')

        if not destination_user.is_phone_validated:
            return response.Response(
                status=status.HTTP_400_BAD_REQUEST,
                data='The user you want to call did not specified or '
                     'validated the phone number')

        source_phone = source_user.normalized_phone
        destination_phone = destination_user.normalized_phone

        proxy_phone = twilio_create_proxy_phone(source_phone, destination_phone)
        if not proxy_phone:
            # TODO: log to sentry because it is our error
            # TODO: something went wrong with proxy number creation
            return response.Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data='Can not create temporary phones for you and user. '
                     'Please repeat it again or ask us for help')

        return response.Response(data={'proxy_phone': proxy_phone})
