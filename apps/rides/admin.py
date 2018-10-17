from django.contrib import admin

from .models import Ride, RideStop, RideBooking, RideComplaint, RideStatus


class RideStatusFilter(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            RideStatus.CHOICES
        )

    def queryset(self, request, queryset):
        return queryset.filter(status=self.value())


class RideAdmin(admin.ModelAdmin):
    list_filter = (RideStatusFilter,)


admin.site.register(RideComplaint)
admin.site.register(Ride, RideAdmin)
admin.site.register(RideStop)
admin.site.register(RideBooking)
