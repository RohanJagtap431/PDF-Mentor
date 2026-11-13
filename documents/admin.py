
from django.contrib import admin
from .models import Document, DocumentAssignment


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "original_filename",
        "file_size",
        "uploaded_by",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "original_filename",
    )

    readonly_fields = (
        "storage_key",
        "file_size",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("PDF Information", {
            "fields": (
                "title",
                "description",
                "original_filename",
                "storage_key",
                "file_size",
            )
        }),
        ("Upload Information", {
            "fields": (
                "uploaded_by",
                "is_active",
                "created_at",
                "updated_at",
            )
        }),
    )


@admin.register(DocumentAssignment)
class DocumentAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "document",
        "user",
        "assigned_by",
        "assigned_at",
        "is_active",
    )

    list_filter = (
        "is_active",
        "assigned_at",
    )

    search_fields = (
        "document__title",
        "user__full_name",
        "user__mobile_number",
    )

    readonly_fields = (
        "assigned_at",
    )
