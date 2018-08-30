from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer, UserUpdateSerializer
from .utils import generate_and_send_sms_code, save_user_code, check_user_code


class MyView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserUpdateSerializer(
            request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(UserSerializer(instance).data)


class ValidatePhoneView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        if not user.phone:
            return Response({'status': 'error', 'error': 'need to fill phone'},
                            status=status.HTTP_400_BAD_REQUEST)
        code = generate_and_send_sms_code(user.phone)
        save_user_code(user.pk, code)
        return Response({'status': 'success'})

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
