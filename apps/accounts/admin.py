from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class MyUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('User fields', {
            'fields': ('age', 'photo', 'phone', 'short_desc')
        }),
    )


admin.site.register(User, MyUserAdmin)
