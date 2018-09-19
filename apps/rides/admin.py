from django.contrib import admin

from .models import Ride, RideStop, RideBooking, RideComplaint


admin.site.register(RideComplaint)
admin.site.register(Ride)
admin.site.register(RideStop)
admin.site.register(RideBooking)
