
from django.urls import path
from . import views

urlpatterns = [

    path(
        "dashboard/",
        views.dashboard_view,
        name="dashboard"
    ),

    path(
        "admin-dashboard/",
        views.admin_dashboard_view,
        name="admin_dashboard"
    ),

    path(
        "admin-users/",
        views.admin_users_view,
        name="admin_users"
    ),

    # View User Details
    path(
        "admin-users/<int:user_id>/",
        views.admin_user_detail_view,
        name="admin_user_detail"
    ),

    # Approve Account
    path(
        "admin-users/<int:user_id>/approve/",
        views.approve_user_view,
        name="approve_user"
    ),

    # Deactivate / Reactivate
    path(
        "admin-users/<int:user_id>/toggle-status/",
        views.toggle_user_status_view,
        name="toggle_user_status"
    ),

    # Set / Reset Password
    path(
        "admin-users/<int:user_id>/password/",
        views.set_user_password_view,
        name="set_user_password"
    ),

    # Delete Account
    path(
        "admin-users/<int:user_id>/delete/",
        views.delete_user_view,
        name="delete_user"
    ),
    
    path(
        "my-pdf-library/",
        views.my_pdf_library_view,
        name="my_pdf_library"
    ),
]
