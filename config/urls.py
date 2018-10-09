from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from djoser import views as djoser_views
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import verify_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter

from apps.accounts.viewsets import UserDetailViewSet
from apps.cars.viewsets import CarViewSet, CarImageViewSet
from apps.places.viewsets import StateViewSet, CityViewSet
from apps.accounts.views import MyView, SendPhoneValidationCodeView,\
    ValidatePhoneView, complete
from apps.rides.viewsets import RideViewSet, \
    RideBookingViewSet, RideRequestViewSet, RideComplaintViewSet
from apps.reviews.viewsets import ReviewViewSet
from apps.flatpages.viewsets import FlatPageViewSet

from .routers import Router


nested_router = SimpleRouter()
nested_router.register('rides/car', CarViewSet, base_name='cars')

car_router = NestedSimpleRouter(
    nested_router, r'rides/car', lookup='car')
car_router.register('images', CarImageViewSet)


router = Router()
router.register('places/state', StateViewSet)
router.register('places/city', CityViewSet)

router.register('rides/ride', RideViewSet)
router.register('rides/booking', RideBookingViewSet)
router.register('rides/request', RideRequestViewSet)
router.register('rides/complaint', RideComplaintViewSet)
router.register('accounts', UserDetailViewSet)
router.register('reviews', ReviewViewSet)
router.register('flatpages', FlatPageViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/my/', MyView.as_view(), name='account_my'),
    path('accounts/send_phone_validation_code/',
         SendPhoneValidationCodeView.as_view(),
         name='account_send_phone_validation_code'),
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
    re_path(r'^accounts/social/complete/(?P<backend>[^/]+)/$',
            complete, name='complete'),
    path('accounts/social/', include('social_django.urls', namespace='social')),
    path('', include(router.urls)),
    path('', include(nested_router.urls)),
    path('', include(car_router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
