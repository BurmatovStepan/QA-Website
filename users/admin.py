from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("login", "password")}),
        ("Personal info", {"fields": ("email", "displayed_name", "avatar", "rating")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    list_display = ("login", "email", "displayed_name", "is_staff", "rating")
    search_fields = ("login", "email", "displayed_name")
    readonly_fields = ("created_at", "last_login", "updated_at")

    ordering = ("login",)

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("login", "email", "password", "password2"),
        }),
    )
