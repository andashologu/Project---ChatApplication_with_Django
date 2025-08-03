#admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm

# Extend UserAdmin to use your CustomUserCreationForm for creating users
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm  # Use your custom form for user creation
    model = CustomUser  # Link to the CustomUser model

    # Fields to display in the admin user list
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    
    # Define the fieldsets for adding and editing users
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    
    # Use this when adding a new user (includes password1 and password2 fields)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
