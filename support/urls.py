
from django.urls import path
from . import views

urlpatterns = [
    path(
        "support/",
        views.support_home_view,
        name="support_home"
    ),

    path(
        "support/create/",
        views.create_ticket_view,
        name="create_ticket"
    ),

    path(
        "support/chat/<int:ticket_id>/",
        views.support_conversation_view,
        name="support_conversation"
    ),
    
    path(
        "admin-support/",
        views.admin_support_inbox_view,
        name="admin_support_inbox"
    ),

    path(
        "admin-support/chat/<int:ticket_id>/",
        views.admin_support_conversation_view,
        name="admin_support_conversation"
    ),

    path(
        "admin-support/chat/<int:ticket_id>/toggle-status/",
        views.admin_toggle_ticket_status_view,
        name="admin_toggle_ticket_status"
    ),

    path(
        "admin-support/chat/<int:ticket_id>/delete/",
        views.admin_delete_ticket_view,
        name="admin_delete_ticket"
    ),
]


