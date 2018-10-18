from django.contrib import admin

from .models import Ride, RideStop, RideBooking, RideComplaint, RideStatus, \
    RideComplaintStatus


class RideStatusFilter(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            RideStatus.CHOICES
        )

    def queryset(self, request, queryset):
        return queryset.filter(status=self.value())


class RideComplaintsFilter(admin.SimpleListFilter):
    title = 'complaints'
    parameter_name = 'complaints'

    def lookups(self, request, model_admin):
        return (
            RideComplaintStatus.CHOICES
        )

    def queryset(self, request, queryset):
        return queryset.filter(complaints__status=self.value())


class ComplaintInline(admin.TabularInline):
    model = RideComplaint
    readonly_fields = ('user', 'description',)
    can_delete = False


class RideAdmin(admin.ModelAdmin):
    list_filter = (RideStatusFilter, RideComplaintsFilter,)

    inlines = [
        ComplaintInline,
    ]


admin.site.register(RideComplaint)
admin.site.register(Ride, RideAdmin)
admin.site.register(RideStop)
admin.site.register(RideBooking)
