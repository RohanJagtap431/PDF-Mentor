
from django.db import models
from django.conf import settings


class Document(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    original_filename = models.CharField(max_length=255)

    # Tigris Object Storage File Key
    storage_key = models.CharField(
        max_length=500,
        unique=True
    )

    file_size = models.PositiveBigIntegerField(default=0)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_documents"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "PDF Document"
        verbose_name_plural = "PDF Documents"

    def __str__(self):
        return self.title


class DocumentAssignment(models.Model):

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="document_assignments"
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_document_assignments"
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["-assigned_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["document", "user"],
                name="unique_document_user_assignment"
            )
        ]

        verbose_name = "PDF Assignment"
        verbose_name_plural = "PDF Assignments"

    def __str__(self):
        return f"{self.document.title} - {self.user.full_name}"
