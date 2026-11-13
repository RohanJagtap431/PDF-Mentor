
import os
import logging
from uuid import uuid4

import boto3

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.views.decorators.http import require_http_methods

from .models import Document, DocumentAssignment

from django.views.decorators.http import require_http_methods, require_POST
from .forms import DocumentUploadForm, DocumentEditForm


logger = logging.getLogger(__name__)
User = get_user_model()


def require_super_admin(user):
    return (
        user.is_authenticated
        and user.is_staff
        and user.is_superuser
    )


def get_tigris_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("AWS_ENDPOINT_URL_S3"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION", "auto"),
    )


@login_required(login_url="login")
@require_http_methods(["GET", "POST"])
def admin_pdf_upload_view(request):

    if not require_super_admin(request.user):
        raise PermissionDenied(
            "Only administrators can upload PDF files."
        )

    if request.method == "POST":

        form = DocumentUploadForm(request.POST, request.FILES)

        if form.is_valid():

            uploaded_file = form.cleaned_data["pdf_file"]
            bucket_name = os.getenv("TIGRIS_BUCKET_NAME")

            if not bucket_name:
                messages.error(
                    request,
                    "Tigris bucket configuration is missing."
                )
                return render(
                    request,
                    "documents/admin_pdf_upload.html",
                    {"form": form}
                )

            storage_key = f"documents/{uuid4().hex}.pdf"
            s3 = get_tigris_client()
            uploaded_to_tigris = False

            try:
                uploaded_file.seek(0)

                s3.upload_fileobj(
                    uploaded_file,
                    bucket_name,
                    storage_key,
                    ExtraArgs={
                        "ContentType": "application/pdf",
                        "ContentDisposition": "inline",
                    },
                    Config=boto3.s3.transfer.TransferConfig(
                        multipart_threshold=8 * 1024 * 1024,
                        multipart_chunksize=8 * 1024 * 1024,
                        max_concurrency=3,
                    )
                )

                uploaded_to_tigris = True

                with transaction.atomic():

                    document = form.save(commit=False)
                    document.original_filename = uploaded_file.name
                    document.storage_key = storage_key
                    document.file_size = uploaded_file.size
                    document.uploaded_by = request.user
                    document.save()

                messages.success(
                    request,
                    "PDF uploaded successfully to Tigris."
                )
                return redirect("admin_pdf_list")

            except Exception:

                logger.exception("Tigris PDF upload failed.")

                if uploaded_to_tigris:
                    try:
                        s3.delete_object(
                            Bucket=bucket_name,
                            Key=storage_key
                        )
                    except Exception:
                        logger.exception(
                            "Tigris cleanup failed for %s",
                            storage_key
                        )

                messages.error(
                    request,
                    "PDF upload failed. Please check Tigris configuration and try again."
                )

    else:
        form = DocumentUploadForm()

    return render(
        request,
        "documents/admin_pdf_upload.html",
        {"form": form}
    )


@login_required(login_url="login")
def admin_pdf_list_view(request):

    if not require_super_admin(request.user):
        raise PermissionDenied(
            "Only administrators can access PDF management."
        )

    documents = Document.objects.all().order_by("-created_at")

    search_query = request.GET.get("search", "").strip()

    if search_query:
        documents = documents.filter(
            title__icontains=search_query
        )

    status = request.GET.get("status", "")

    if status == "active":
        documents = documents.filter(is_active=True)
    elif status == "inactive":
        documents = documents.filter(is_active=False)

    paginator = Paginator(documents, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "documents": page_obj,
        "page_obj": page_obj,
        "search_query": search_query,
        "selected_status": status,
        "total_documents": Document.objects.count(),
        "active_documents": Document.objects.filter(
            is_active=True
        ).count(),
        "inactive_documents": Document.objects.filter(
            is_active=False
        ).count(),
    }

    return render(
        request,
        "documents/admin_pdf_list.html",
        context
    )


@login_required(login_url="login")
@require_http_methods(["GET", "POST"])
def admin_pdf_assign_view(request):

    if not require_super_admin(request.user):
        raise PermissionDenied(
            "Only administrators can assign PDF files."
        )

    users = User.objects.filter(
        role="user",
        is_staff=False,
        is_superuser=False,
        is_active=True,
        is_approved=True,
    ).order_by("full_name")

    documents = Document.objects.filter(
        is_active=True
    ).order_by("title")

    if request.method == "POST":

        user_id = request.POST.get("user_id")
        document_ids = request.POST.getlist("document_ids")

        selected_user = get_object_or_404(
            users,
            pk=user_id
        ) if user_id else None

        if not selected_user:
            messages.error(request, "Please select a user.")

        elif not document_ids:
            messages.error(request, "Please select at least one PDF.")

        else:

            selected_documents = documents.filter(
                id__in=document_ids
            )

            if selected_documents.count() != len(set(document_ids)):
                messages.error(
                    request,
                    "One or more selected PDFs are invalid or inactive."
                )
            else:

                with transaction.atomic():

                    for document in selected_documents:

                        assignment, created = (
                            DocumentAssignment.objects.get_or_create(
                                document=document,
                                user=selected_user,
                                defaults={
                                    "assigned_by": request.user,
                                    "is_active": True,
                                }
                            )
                        )

                        if not created:
                            assignment.is_active = True
                            assignment.assigned_by = request.user
                            assignment.save(
                                update_fields=[
                                    "is_active",
                                    "assigned_by",
                                ]
                            )

                messages.success(
                    request,
                    f"PDFs assigned successfully to {selected_user.full_name}."
                )

                return redirect("admin_pdf_assign")

    assignments = DocumentAssignment.objects.select_related(
        "document",
        "user",
        "assigned_by",
    ).order_by("-assigned_at")

    context = {
        "users": users,
        "documents": documents,
        "assignments": assignments,
    }

    return render(
        request,
        "documents/admin_pdf_assign.html",
        context
    )


@login_required(login_url="login")
def document_view(request, document_id):

    document = get_object_or_404(
        Document,
        id=document_id,
        is_active=True,
    )

    is_admin = require_super_admin(request.user)

    if not is_admin:

        if not request.user.is_active or not getattr(
            request.user, "is_approved", False
        ):
            raise PermissionDenied(
                "Your account is not active or approved."
            )

        has_access = DocumentAssignment.objects.filter(
            document=document,
            user=request.user,
            is_active=True,
        ).exists()

        if not has_access:
            raise PermissionDenied(
                "You do not have permission to view this PDF."
            )

    bucket_name = os.getenv("TIGRIS_BUCKET_NAME")

    if not bucket_name:
        logger.error("Tigris bucket configuration is missing.")
        raise PermissionDenied(
            "PDF storage is currently unavailable."
        )

    try:

        s3 = get_tigris_client()

        signed_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket_name,
                "Key": document.storage_key,
                "ResponseContentType": "application/pdf",
                "ResponseContentDisposition": "inline",
            },
            ExpiresIn=120,
        )

        return redirect(signed_url)

    except Exception:

        logger.exception(
            "Unable to generate PDF viewing URL for document %s",
            document.id,
        )

        messages.error(
            request,
            "Unable to open this PDF right now. Please try again."
        )

        return redirect("dashboard")


@login_required(login_url="login")
@require_http_methods(["POST"])
def remove_pdf_assignment_view(request, assignment_id):

    if not require_super_admin(request.user):
        raise PermissionDenied(
            "Only administrators can remove PDF assignments."
        )

    assignment = get_object_or_404(
        DocumentAssignment,
        id=assignment_id
    )

    assignment.is_active = False
    assignment.save(update_fields=["is_active"])

    messages.success(
        request,
        f"Access to '{assignment.document.title}' removed for {assignment.user.full_name}."
    )

    return redirect("admin_pdf_assign")


@login_required(login_url="login")
@require_http_methods(["GET", "POST"])
def admin_pdf_edit_view(request, document_id):

    if not require_super_admin(request.user):
        raise PermissionDenied(
            "Only administrators can edit PDFs."
        )

    document = get_object_or_404(
        Document,
        id=document_id
    )

    if request.method == "POST":
        form = DocumentEditForm(
            request.POST,
            instance=document
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "PDF details updated successfully."
            )

            return redirect("admin_pdf_list")

    else:
        form = DocumentEditForm(instance=document)

    return render(
        request,
        "documents/admin_pdf_edit.html",
        {
            "form": form,
            "document": document,
        }
    )


@login_required(login_url="login")
@require_POST
def admin_pdf_toggle_status_view(request, document_id):

    if not require_super_admin(request.user):
        raise PermissionDenied(
            "Only administrators can change PDF status."
        )

    document = get_object_or_404(
        Document,
        id=document_id
    )

    document.is_active = not document.is_active

    document.save(update_fields=["is_active"])

    if document.is_active:
        messages.success(
            request,
            f"'{document.title}' activated successfully."
        )
    else:
        messages.success(
            request,
            f"'{document.title}' deactivated successfully."
        )

    return redirect("admin_pdf_list")


@login_required(login_url="login")
@require_POST
def admin_pdf_delete_view(request, document_id):

    if not require_super_admin(request.user):
        raise PermissionDenied(
            "Only administrators can delete PDFs."
        )

    document = get_object_or_404(
        Document,
        id=document_id
    )

    bucket_name = os.getenv("TIGRIS_BUCKET_NAME")

    if not bucket_name:
        messages.error(
            request,
            "Tigris bucket configuration is missing."
        )
        return redirect("admin_pdf_list")

    try:
        s3 = get_tigris_client()

        # Delete the PDF from Tigris first.
        s3.delete_object(
            Bucket=bucket_name,
            Key=document.storage_key
        )

        # Delete database record and related assignments.
        document_title = document.title
        document.delete()

        messages.success(
            request,
            f"'{document_title}' deleted successfully."
        )

    except Exception:
        logger.exception(
            "PDF deletion failed for document %s",
            document_id
        )

        messages.error(
            request,
            "PDF deletion failed. Please check Tigris configuration and try again."
        )

    return redirect("admin_pdf_list")
