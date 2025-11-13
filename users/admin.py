from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Activity, CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    def has_add_permission(self, request):
        return False

    fieldsets = (
        (None, {"fields": ("login", "password")}),
        ("Personal info", {"fields": ("email", "display_name", "avatar", "rating")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    list_display = ("login", "email", "display_name", "is_staff", "rating")
    search_fields = ("login", "email", "display_name")
    readonly_fields = ("created_at", "last_login", "updated_at")

    ordering = ("login",)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("user", "type")}),
        ("Linked action", {"fields": ("content_type", "object_id", "target")}),
        ("Important dates", {"fields": ("created_at",)}),
    )

    add_fieldsets = (
        (None, {"fields": ("user", "type")}),
        ("Linked action", {"fields": ("content_type", "object_id")}),
        ("Important dates", {"fields": ("created_at",)}),
    )

    readonly_fields = ("target", "created_at")

    list_display = ("user", "type", "target", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("user__login",)

    ordering = ("-created_at",)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets
        return self.fieldsets

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
             return self.readonly_fields + ("user", "type", "content_type", "object_id")
        return self.readonly_fields
