from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Metric, Record


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Fields to display in the admin list view
    list_display = ("username", "email", "is_admin", "is_staff", "is_active")

    # Fields to filter by in the admin list view
    list_filter = ("is_admin", "is_staff", "is_active")

    # Fields to be used in the admin detail view
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_admin",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Fields to be used when creating a new user in the admin portal
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_admin",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    # Ordering for list view
    ordering = ("username",)

    # Search fields
    search_fields = ("username", "email")


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    # Ensure fields in list_display exist in the Metric model
    list_display = (
        "id",
        "name",
        "description",
        "target",
    )  # Update to match your Metric model fields
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ("id", "metric", "team", "value", "recorded_at", "timestamp")
    search_fields = ("metric__name", "team__name")
    list_filter = ("metric", "team", "recorded_at")
