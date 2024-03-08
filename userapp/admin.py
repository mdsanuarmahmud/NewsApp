from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *  # Replace with your custom user model

# admin.site.register(AppUser)

# Changing the Django Admin Header Text
admin.site.site_header = 'AI News Writing Project'   


# Custom Admin View for User Management
# Included password Reset Fields
class AppUserAdmin(UserAdmin):
    model = AppUser
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
            (None, {'fields': ('username', 'password')}),
            ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
            ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
            ('Important dates', {'fields': ('last_login', 'date_joined')}),
        )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


admin.site.register(AppUser, AppUserAdmin)

