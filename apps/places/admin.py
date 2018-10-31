from django.contrib import admin

from .models import State, City, Place


class CityAdmin(admin.ModelAdmin):
    list_filter = ('state', )
    search_fields = ('name', )


class PlaceAdmin(admin.ModelAdmin):
    list_filter = ('category', )
    search_fields = ('name', 'short_name', 'city', )


admin.site.register(State)
admin.site.register(City, CityAdmin)
admin.site.register(Place, PlaceAdmin)
