
from django.contrib import admin
from .models import SupportTicket, SupportMessage


class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "subject",
        "status",
        "created_at",
        "updated_at",
    )

    list_filter = ("status", "created_at")

    search_fields = (
        "user__full_name",
        "user__mobile_number",
        "subject",
    )

    inlines = [SupportMessageInline]


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "ticket",
        "sender",
        "sender_type",
        "is_read",
        "created_at",
    )

    list_filter = ("sender_type", "is_read")
