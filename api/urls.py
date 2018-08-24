from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from djoser import views as djoser_views
from rest_framework.routers import DefaultRouter

from apps.places.viewsets import StateViewSet, CityViewSet
from apps.accounts.views import MyView
from apps.rides.viewsets import CarViewSet, RideViewSet, \
    RideBookingViewSet, RideRequestViewSet


router = DefaultRouter()
router.register('places/state', StateViewSet)
router.register('places/city', CityViewSet)

router.register('rides/car', CarViewSet)
router.register('rides/ride', RideViewSet)
router.register('rides/booking', RideBookingViewSet)
router.register('rides/request', RideRequestViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/my/', MyView.as_view()),
    # Registration
    path('accounts/register/', djoser_views.UserCreateView.as_view()),
    path('accounts/activate/', djoser_views.ActivationView.as_view()),
    path('accounts/password/reset/', djoser_views.PasswordResetView.as_view()),
    path('accounts/password/reset/confirm/',
         djoser_views.PasswordResetConfirmView.as_view()),
] + router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
