from django.contrib import admin

from .models import Car, Ride, RideBooking


admin.site.register(Car)
admin.site.register(Ride)
admin.site.register(RideBooking)
