from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter, APIRootView


class RootView(APIRootView):
    def get(self, request, *args, **kwargs):
        old_response = super(RootView, self).get(request, *args, **kwargs)
        data = old_response.data
        data['accounts/login'] = reverse('account_jwt_login', request=request)
        data['accounts/login/facebook'] = reverse('social:begin',
                                                  args=('google-oauth2',),
                                                  request=request)
        data['accounts/verify'] = reverse('account_jwt_verify', request=request)
        data['accounts/refresh'] = reverse('account_jwt_refresh',
                                           request=request)
        data['accounts/my'] = reverse('account_my', request=request)
        data['accounts/register'] = reverse('account_register', request=request)
        data['accounts/activate'] = reverse('account_activate', request=request)
        data['accounts/password/reset'] = reverse(
            'account_password_reset', request=request)
        data['accounts/password/reset/confirm'] = reverse(
            'account_password_confirm', request=request)

        return Response(data)


class Router(DefaultRouter):
    APIRootView = RootView
