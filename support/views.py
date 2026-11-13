
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction

from .models import SupportTicket, SupportMessage


# ==========================================
# USER ACCOUNT CHECK
# ==========================================

def check_support_user(request):

    user = request.user

    if not user.is_active or not user.is_approved:
        messages.error(
            request,
            "Your account is not approved or is inactive."
        )
        return False

    if user.is_staff:
        return False

    return True


# ==========================================
# SUPPORT HOME
# ==========================================

@login_required(login_url="login")
def support_home_view(request):

    if not check_support_user(request):
        return redirect("login") if not request.user.is_staff else redirect("admin_dashboard")

    tickets = SupportTicket.objects.filter(
        user=request.user
    ).prefetch_related("messages")

    context = {
        "tickets": tickets,
    }

    return render(
        request,
        "support/support_home.html",
        context
    )


# ==========================================
# CREATE NEW SUPPORT CONVERSATION
# ==========================================

@login_required(login_url="login")
@require_POST
def create_ticket_view(request):

    if not check_support_user(request):
        return redirect("login") if not request.user.is_staff else redirect("admin_dashboard")

    subject = request.POST.get("subject", "").strip()
    message_text = request.POST.get("message", "").strip()

    if not subject:
        subject = "General Support"

    if not message_text:
        messages.error(request, "Please enter your message.")
        return redirect("support_home")

    if len(message_text) > 10000:
        messages.error(request, "Message is too long.")
        return redirect("support_home")

    with transaction.atomic():

        ticket = SupportTicket.objects.create(
            user=request.user,
            subject=subject[:200],
            status="open"
        )

        SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            sender_type="user",
            message=message_text,
            is_read=False
        )

    messages.success(
        request,
        "Your support conversation has been created."
    )

    return redirect(
        "support_conversation",
        ticket_id=ticket.id
    )


# ==========================================
# USER CONVERSATION
# ==========================================

@login_required(login_url="login")
def support_conversation_view(request, ticket_id):

    if not check_support_user(request):
        return redirect("login") if not request.user.is_staff else redirect("admin_dashboard")

    ticket = get_object_or_404(
        SupportTicket,
        id=ticket_id,
        user=request.user
    )

    # Mark admin replies as read by user
    SupportMessage.objects.filter(
        ticket=ticket,
        sender_type="admin",
        is_read=False
    ).update(is_read=True)

    if request.method == "POST":

        message_text = request.POST.get(
            "message", ""
        ).strip()

        if ticket.status == "closed":

            messages.error(
                request,
                "This conversation is closed. Please start a new conversation."
            )

        elif not message_text:

            messages.error(
                request,
                "Please enter a message."
            )

        elif len(message_text) > 10000:

            messages.error(
                request,
                "Message is too long."
            )

        else:

            SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                sender_type="user",
                message=message_text,
                is_read=False
            )

            messages.success(
                request,
                "Message sent successfully."
            )

        return redirect(
            "support_conversation",
            ticket_id=ticket.id
        )

    conversation_messages = ticket.messages.select_related(
        "sender"
    ).all()

    context = {
        "ticket": ticket,
        "conversation_messages": conversation_messages,
    }

    return render(
        request,
        "support/conversation.html",
        context
    )


# ==========================================
# ADMIN PERMISSION
# ==========================================

def check_support_admin(request):

    user = request.user

    return (
        user.is_authenticated
        and user.is_active
        and user.is_staff
        and user.is_superuser
    )


# ==========================================
# ADMIN SUPPORT INBOX
# ==========================================

@login_required(login_url="login")
def admin_support_inbox_view(request):

    if not check_support_admin(request):
        return redirect("admin_dashboard")

    tickets = SupportTicket.objects.select_related(
        "user"
    ).prefetch_related("messages")

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        from django.db.models import Q

        tickets = tickets.filter(
            Q(user__full_name__icontains=search)
            | Q(user__mobile_number__icontains=search)
            | Q(subject__icontains=search)
        )

    if status in ["open", "closed"]:
        tickets = tickets.filter(status=status)

    context = {
        "tickets": tickets,
        "search": search,
        "selected_status": status,
        "total_tickets": SupportTicket.objects.count(),
        "open_tickets": SupportTicket.objects.filter(
            status="open"
        ).count(),
        "closed_tickets": SupportTicket.objects.filter(
            status="closed"
        ).count(),
        "unread_messages": SupportMessage.objects.filter(
            sender_type="user",
            is_read=False
        ).count(),
    }

    return render(
        request,
        "support/admin/inbox.html",
        context
    )


# ==========================================
# ADMIN CHAT CONVERSATION
# ==========================================

@login_required(login_url="login")
def admin_support_conversation_view(request, ticket_id):

    if not check_support_admin(request):
        return redirect("admin_dashboard")

    ticket = get_object_or_404(
        SupportTicket.objects.select_related("user"),
        id=ticket_id
    )

    # Mark user messages as read
    SupportMessage.objects.filter(
        ticket=ticket,
        sender_type="user",
        is_read=False
    ).update(is_read=True)

    if request.method == "POST":

        message_text = request.POST.get(
            "message", ""
        ).strip()

        if ticket.status == "closed":

            messages.error(
                request,
                "This ticket is closed. Reopen it before replying."
            )

        elif not message_text:

            messages.error(
                request,
                "Please enter a reply."
            )

        elif len(message_text) > 10000:

            messages.error(
                request,
                "Message is too long."
            )

        else:

            SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                sender_type="admin",
                message=message_text,
                is_read=False
            )

            ticket.save(update_fields=["updated_at"])

            messages.success(
                request,
                "Reply sent successfully."
            )

        return redirect(
            "admin_support_conversation",
            ticket_id=ticket.id
        )

    conversation_messages = ticket.messages.select_related(
        "sender"
    ).all()

    context = {
        "ticket": ticket,
        "conversation_messages": conversation_messages,
    }

    return render(
        request,
        "support/admin/conversation.html",
        context
    )


# ==========================================
# ADMIN CLOSE / REOPEN TICKET
# ==========================================

@login_required(login_url="login")
@require_POST
def admin_toggle_ticket_status_view(request, ticket_id):

    if not check_support_admin(request):
        return redirect("admin_dashboard")

    ticket = get_object_or_404(
        SupportTicket,
        id=ticket_id
    )

    ticket.status = (
        "closed" if ticket.status == "open" else "open"
    )

    ticket.save()

    messages.success(
        request,
        f"Ticket status changed to {ticket.get_status_display()}."
    )

    return redirect(
        "admin_support_conversation",
        ticket_id=ticket.id
    )


# ==========================================
# ADMIN DELETE COMPLETE CHAT HISTORY
# ==========================================

@login_required(login_url="login")
@require_POST
def admin_delete_ticket_view(request, ticket_id):

    if not check_support_admin(request):
        return redirect("admin_dashboard")

    ticket = get_object_or_404(
        SupportTicket,
        id=ticket_id
    )

    with transaction.atomic():
        ticket.delete()

    messages.success(
        request,
        "Support ticket and complete chat history deleted successfully."
    )

    return redirect("admin_support_inbox")