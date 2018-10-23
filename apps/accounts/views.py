from django.conf import settings
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler
from social_django.utils import psa

from apps.main.utils import send_sms
from .serializers import UserSerializer, UserUpdateSerializer
from .utils import generate_sms_code, save_user_code, check_user_code


class MyView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(
            UserSerializer(request.user, context={'request': request}).data)

    def put(self, request):
        serializer = UserUpdateSerializer(
            request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            UserSerializer(instance, context={'request': request}).data)


class SendPhoneValidationCodeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        if not user.phone:
            return Response(
                {'status': 'error', 'error': 'need to fill phone'},
                status=status.HTTP_400_BAD_REQUEST)
        code = generate_sms_code()
        send_sms(
            'phone_validate',
            user.normalized_phone,
            {'code': code}
        )
        save_user_code(user.pk, code)
        return Response({'status': 'success'})


class ValidatePhoneView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        code = request.data.get('code', '')
        if check_user_code(user.pk, code):
            user.is_phone_validated = True
            user.save(update_fields=['is_phone_validated'])
            return Response({'status': 'success'})
        else:
            return Response({'status': 'error', 'error': 'invalid code'},
                            status=status.HTTP_400_BAD_REQUEST)


@never_cache
@csrf_exempt
@psa('complete')
def complete(request, backend, *args, **kwargs):
    """Authentication complete view"""

    # TODO: think about inactive users
    user = request.backend.complete(*args, **kwargs)

    if user:
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        url = "{0}?token={1}".format(settings.LOGIN_REDIRECT_URL, token)
    else:
        url = settings.LOGIN_ERROR_URL

    return request.backend.strategy.redirect(url)
