from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models.user_models import User


class CustomUserAdmin(UserAdmin):
    """ Custom admin panel for User model """
    
    model = User
    list_display = ("email", "first_name", "last_name", "group", "is_staff", "is_active")
    list_filter = ("group", "is_staff", "is_active")
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone_no", "gender", "dob", "designation", "department", "address", "profile_pic")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Role", {"fields": ("group",)}),  # Added group field
        ("Important Dates", {"fields": ("last_login", "date_joined", "created_at", "modified_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "first_name", "last_name", "phone_no", "gender", "dob", "designation", "group", "is_staff", "is_active"),
        }),
    )


admin.site.register(User, CustomUserAdmin)