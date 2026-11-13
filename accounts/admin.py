
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User
from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        "full_name",
        "mobile_number",
        "role",
        "is_approved",
        "is_active",
        "date_joined",
    )

    list_filter = (
        "role",
        "is_approved",
        "is_active",
    )

    search_fields = (
        "full_name",
        "mobile_number",
    )

    ordering = ("-date_joined",)

    readonly_fields = (
        "last_login",
        "date_joined",
    )

    fieldsets = (
        ("Personal Information", {
            "fields": (
                "full_name",
                "mobile_number",
                "password",
            )
        }),

        ("Account Management", {
            "fields": (
                "role",
                "is_approved",
                "is_active",
            )
        }),

        ("Permissions", {
            "fields": (
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),

        ("Important Dates", {
            "fields": (
                "last_login",
                "date_joined",
            )
        }),
    )

    add_fieldsets = (
        ("Create New User", {
            "classes": ("wide",),
            "fields": (
                "full_name",
                "mobile_number",
                "password1",
                "password2",
                "role",
                "is_approved",
                "is_active",
            ),
        }),
    )

    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    list_per_page = 25
