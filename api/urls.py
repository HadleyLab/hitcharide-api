from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter

from apps.places.viewsets import StateViewSet, CityViewSet
from apps.accounts.views import MyView
from apps.rides.viewsets import CarViewSet, RideViewSet, RideBookingViewSet


router = DefaultRouter()
router.register('places/state', StateViewSet)
router.register('places/city', CityViewSet)

router.register('rides/car', CarViewSet)
router.register('rides/ride', RideViewSet)
router.register('rides/booking', RideBookingViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/my/', MyView.as_view()),
] + router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
