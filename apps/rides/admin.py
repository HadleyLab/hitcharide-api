from django.contrib import admin

from .models import Car, Ride, RidePoint, RideBooking


admin.site.register(Car)
admin.site.register(Ride)
admin.site.register(RidePoint)
admin.site.register(RideBooking)
