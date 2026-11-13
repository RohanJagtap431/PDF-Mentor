
from django.urls import path
from . import views

urlpatterns = [
    # Admin PDF Management
    path(
        "admin-pdfs/",
        views.admin_pdf_list_view,
        name="admin_pdf_list"
    ),

    path(
        "admin-pdfs/upload/",
        views.admin_pdf_upload_view,
        name="admin_pdf_upload"
    ),

    path(
        "admin-pdfs/assign/",
        views.admin_pdf_assign_view,
        name="admin_pdf_assign"
    ),

    # Secure PDF Viewer
    path(
        "pdf/<int:document_id>/view/",
        views.document_view,
        name="document_view"
    ),
    
    path(
        "admin-pdfs/assign/<int:assignment_id>/remove/",
        views.remove_pdf_assignment_view,
        name="remove_pdf_assignment"
    ),
    
    
    path(
        "admin-pdfs/<int:document_id>/edit/",
        views.admin_pdf_edit_view,
        name="admin_pdf_edit"
    ),

    path(
        "admin-pdfs/<int:document_id>/toggle-status/",
        views.admin_pdf_toggle_status_view,
        name="admin_pdf_toggle_status"
    ),

    path(
        "admin-pdfs/<int:document_id>/delete/",
        views.admin_pdf_delete_view,
        name="admin_pdf_delete"
    ),

]
