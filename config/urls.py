from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from djoser import views as djoser_views
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import verify_jwt_token
from rest_framework_jwt.views import refresh_jwt_token

from apps.places.viewsets import StateViewSet, CityViewSet
from apps.accounts.views import MyView, ValidatePhoneView
from apps.rides.viewsets import CarViewSet, RideViewSet, \
    RideBookingViewSet, RideRequestViewSet

from .routers import Router


router = Router()
router.register('places/state', StateViewSet)
router.register('places/city', CityViewSet)

router.register('rides/car', CarViewSet)
router.register('rides/ride', RideViewSet)
router.register('rides/booking', RideBookingViewSet)
router.register('rides/request', RideRequestViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/my/', MyView.as_view(), name='account_my'),
    path('accounts/validate_phone/',
         ValidatePhoneView.as_view(),
         name='account_validate_phone'),

    path('accounts/login/', obtain_jwt_token, name='account_jwt_login'),
    path('accounts/verify/', verify_jwt_token, name='account_jwt_verify'),
    path('accounts/refresh/', refresh_jwt_token, name='account_jwt_refresh'),

    path('accounts/register/', djoser_views.UserCreateView.as_view(),
         name='account_register'),
    path('accounts/activate/', djoser_views.ActivationView.as_view(),
         name='account_activate'),
    path('accounts/password/reset/', djoser_views.PasswordResetView.as_view(),
         name='account_password_reset'),
    path('accounts/password/reset/confirm/',
         djoser_views.PasswordResetConfirmView.as_view(),
         name='account_password_confirm'),

    path('accounts/rest/', include('rest_framework.urls')),
    path('accounts/social/', include('rest_framework_social_oauth2.urls')),
] + router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
