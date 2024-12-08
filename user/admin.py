from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import User
from django.utils.translation import gettext_lazy as _


class CustomUserAdmin(UserAdmin):
    # Define the fieldsets to customize the user form layout
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'age', 'gender')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    # Define the list of fields to display in the user list view
    list_display = (
    'email', 'first_name', 'last_name', 'age', 'gender', 'is_staff', 'is_active', 'created_at', 'updated_at')

    # Define the fields to filter the user list by
    list_filter = ('is_active', 'is_staff', 'gender')

    # Allow searching by email and first_name
    search_fields = ('email', 'first_name', 'last_name')

    # Customize the form for creating and updating users
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'email', 'password1', 'password2', 'first_name', 'last_name', 'age', 'gender', 'is_staff', 'is_active')
        }),
    )

    # Make sure the custom user model is used for creating users
    ordering = ('email',)
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_by')


# Register the custom user model with the admin
admin.site.register(User, CustomUserAdmin)