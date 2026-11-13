
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from documents.models import DocumentAssignment


User = get_user_model()


# ==========================================
# USER DASHBOARD
# ==========================================

@login_required(login_url="login")
def dashboard_view(request):

    user = request.user

    # Inactive account protection
    if not user.is_active:
        logout(request)
        messages.error(request, "Your account is inactive.")
        return redirect("login")

    # Approval protection
    if not user.is_approved:
        logout(request)
        messages.warning(
            request,
            "Your account is waiting for admin approval."
        )
        return redirect("login")

    # Admin redirection
    if user.is_superuser and user.is_staff:
        return redirect("admin_dashboard")

    # Other staff accounts
    if user.is_staff:
        return redirect("admin:index")

    # Get PDFs assigned to this user
    assignments = DocumentAssignment.objects.filter(
        user=user,
        is_active=True,
        document__is_active=True,
    ).select_related(
        "document"
    ).order_by("-assigned_at")

    total_assigned_pdfs = assignments.count()

    paginator = Paginator(assignments, 8)

    my_assignments = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "current_user": user,
        "my_assignments": my_assignments,
        "total_assigned_pdfs": total_assigned_pdfs,
    }

    return render(
        request,
        "dashboard/index.html",
        context
    )



@login_required(login_url="login")
def my_pdf_library_view(request):

    user = request.user

    if not user.is_active or not user.is_approved:
        logout(request)
        messages.error(request, "Your account is inactive or not approved.")
        return redirect("login")

    if user.is_staff:
        if user.is_superuser:
            return redirect("admin_dashboard")
        return redirect("admin:index")

    assignments = DocumentAssignment.objects.filter(
        user=user,
        is_active=True,
        document__is_active=True,
    ).select_related(
        "document"
    ).order_by("-assigned_at")

    search_query = request.GET.get("search", "").strip()

    if search_query:
        assignments = assignments.filter(
            document__title__icontains=search_query
        )

    total_pdfs = assignments.count()

    paginator = Paginator(assignments, 12)

    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "current_user": user,
        "my_assignments": page_obj,
        "total_pdfs": total_pdfs,
        "search_query": search_query,
    }

    return render(
        request,
        "dashboard/my_pdf_library.html",
        context
    )



# ==========================================
# ADMIN DASHBOARD
# ==========================================

@login_required(login_url="login")
def admin_dashboard_view(request):

    user = request.user

    # Only Superuser Admin can access
    if not (
        user.is_authenticated
        and user.is_staff
        and user.is_superuser
    ):
        raise PermissionDenied(
            "You are not authorized to access this page."
        )

    # User Statistics
    total_users = User.objects.filter(
        role="user"
    ).count()

    approved_users = User.objects.filter(
        role="user",
        is_approved=True,
        is_active=True
    ).count()

    pending_users = User.objects.filter(
        role="user",
        is_approved=False
    ).count()

    inactive_users = User.objects.filter(
        role="user",
        is_active=False
    ).count()

    # Recent Registrations
    recent_users = User.objects.filter(
        role="user"
    ).order_by("-date_joined")[:5]

    # Admin Statistics
    total_admins = User.objects.filter(
        is_superuser=True,
        is_staff=True
    ).count()

    context = {
        "admin_user": user,

        "total_users": total_users,
        "approved_users": approved_users,
        "pending_users": pending_users,
        "inactive_users": inactive_users,
        "total_admins": total_admins,

        "recent_users": recent_users,

        "current_time": timezone.localtime(),
    }

    return render(
        request,
        "dashboard/admin_dashboard.html",
        context
    )


# ==========================================
# ADMIN USER MANAGEMENT
# ==========================================

@login_required(login_url="login")
def admin_users_view(request):

    user = request.user

    # Only Superuser Admin
    if not (user.is_staff and user.is_superuser):
        raise PermissionDenied(
            "You are not authorized to access this page."
        )

    # Only regular users
    users = User.objects.filter(
        role="user"
    ).order_by("-date_joined")

    # Search
    search_query = request.GET.get("search", "").strip()

    if search_query:
        users = users.filter(
            Q(full_name__icontains=search_query) |
            Q(mobile_number__icontains=search_query)
        )

    # Status Filter
    status = request.GET.get("status", "").strip()

    if status == "approved":
        users = users.filter(
            is_approved=True,
            is_active=True
        )

    elif status == "pending":
        users = users.filter(
            is_approved=False,
            is_active=True
        )

    elif status == "inactive":
        users = users.filter(
            is_active=False
        )

    # Pagination
    paginator = Paginator(users, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "admin_user": user,
        "users": page_obj,
        "page_obj": page_obj,
        "search_query": search_query,
        "selected_status": status,

        "total_users": User.objects.filter(
            role="user"
        ).count(),

        "approved_count": User.objects.filter(
            role="user",
            is_approved=True,
            is_active=True
        ).count(),

        "pending_count": User.objects.filter(
            role="user",
            is_approved=False,
            is_active=True
        ).count(),

        "inactive_count": User.objects.filter(
            role="user",
            is_active=False
        ).count(),
    }

    return render(
        request,
        "dashboard/admin_users.html",
        context
    )


# ==========================================
# ADMIN USER ACTIONS
# ==========================================

def get_managed_user(user_id):
    """
    Only regular user accounts can be managed here.
    Staff and superuser accounts are protected.
    """

    return get_object_or_404(
        User,
        pk=user_id,
        role="user",
        is_staff=False,
        is_superuser=False
    )


def check_admin_permission(request):
    """
    Only authenticated superuser administrators.
    """

    if not (
        request.user.is_authenticated
        and request.user.is_staff
        and request.user.is_superuser
    ):
        raise PermissionDenied(
            "You are not authorized to perform this action."
        )


# ==========================================
# 1. VIEW USER DETAILS
# ==========================================

@login_required(login_url="login")
def admin_user_detail_view(request, user_id):

    check_admin_permission(request)

    managed_user = get_managed_user(user_id)

    context = {
        "admin_user": request.user,
        "managed_user": managed_user,
    }

    return render(
        request,
        "dashboard/admin_user_detail.html",
        context
    )


# ==========================================
# 2. APPROVE USER ACCOUNT
# ==========================================

@login_required(login_url="login")
@require_POST
def approve_user_view(request, user_id):

    check_admin_permission(request)

    managed_user = get_managed_user(user_id)

    if not managed_user.is_active:
        messages.error(
            request,
            "Activate this account before approving it."
        )
        return redirect("admin_users")

    if managed_user.is_approved:
        messages.info(
            request,
            "This account is already approved."
        )
        return redirect("admin_users")

    managed_user.is_approved = True

    managed_user.save(
        update_fields=["is_approved"]
    )

    messages.success(
        request,
        f"{managed_user.full_name}'s account has been approved."
    )

    return redirect("admin_users")


# ==========================================
# 3. DEACTIVATE / REACTIVATE USER
# ==========================================

@login_required(login_url="login")
@require_POST
def toggle_user_status_view(request, user_id):

    check_admin_permission(request)

    managed_user = get_managed_user(user_id)

    managed_user.is_active = not managed_user.is_active

    managed_user.save(
        update_fields=["is_active"]
    )

    if managed_user.is_active:
        messages.success(
            request,
            f"{managed_user.full_name}'s account has been reactivated."
        )

    else:
        messages.warning(
            request,
            f"{managed_user.full_name}'s account has been deactivated."
        )

    return redirect("admin_users")


# ==========================================
# 4. SET / RESET USER PASSWORD
# ==========================================

@login_required(login_url="login")
def set_user_password_view(request, user_id):

    check_admin_permission(request)

    managed_user = get_managed_user(user_id)

    if request.method == "POST":

        password = request.POST.get("password", "")

        confirm_password = request.POST.get(
            "confirm_password", ""
        )

        if not password or not confirm_password:
            messages.error(
                request,
                "Both password fields are required."
            )

        elif password != confirm_password:
            messages.error(
                request,
                "Passwords do not match."
            )

        else:
            try:
                validate_password(password, managed_user)

                managed_user.set_password(password)

                managed_user.save(
                    update_fields=["password"]
                )

                messages.success(
                    request,
                    f"Password updated successfully for {managed_user.full_name}."
                )

                return redirect("admin_users")

            except ValidationError as error:
                for message in error.messages:
                    messages.error(request, message)

    context = {
        "admin_user": request.user,
        "managed_user": managed_user,
    }

    return render(
        request,
        "dashboard/admin_user_password.html",
        context
    )


# ==========================================
# 5. DELETE USER ACCOUNT
# ==========================================

@login_required(login_url="login")
@require_POST
def delete_user_view(request, user_id):

    check_admin_permission(request)

    managed_user = get_managed_user(user_id)

    user_name = managed_user.full_name

    managed_user.delete()

    messages.success(
        request,
        f"{user_name}'s account has been permanently deleted."
    )

    return redirect("admin_users")
