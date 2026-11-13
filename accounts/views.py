
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .forms import UserRegistrationForm


# ==========================================
# HELPER: REDIRECT USER BASED ON ROLE
# ==========================================

def redirect_user(user):

    if user.is_superuser and user.is_staff:
        return redirect("admin_dashboard")

    if user.is_staff:
        return redirect("admin:index")

    return redirect("dashboard")


# ==========================================
# USER REGISTRATION
# ==========================================

def register_view(request):

    if request.user.is_authenticated:
        return redirect_user(request.user)

    if request.method == "POST":

        form = UserRegistrationForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.is_approved = False
            user.is_active = True
            user.role = "user"

            # Admin will set password after registration
            user.set_unusable_password()

            user.save()

            messages.success(
                request,
                "Registration successful! Please wait for admin approval."
            )

            return redirect("login")

    else:
        form = UserRegistrationForm()

    context = {
        "form": form
    }

    return render(
        request,
        "accounts/register.html",
        context
    )


# ==========================================
# USER LOGIN
# ==========================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect_user(request.user)

    if request.method == "POST":

        mobile_number = request.POST.get(
            "mobile_number", ""
        ).strip()

        password = request.POST.get(
            "password", ""
        )

        user = authenticate(
            request,
            username=mobile_number,
            password=password
        )

        if user is not None:

            # Check account status
            if not user.is_active:

                messages.error(
                    request,
                    "Your account is inactive. Contact admin."
                )

            elif not user.is_approved:

                messages.error(
                    request,
                    "Your account is waiting for admin approval."
                )

            else:

                login(request, user)

                return redirect_user(user)

        else:

            messages.error(
                request,
                "Invalid mobile number or password."
            )

    return render(
        request,
        "accounts/login.html"
    )


# ==========================================
# USER DASHBOARD
# ==========================================

@login_required(login_url="login")
def dashboard_view(request):

    user = request.user

    # Admin redirection
    if user.is_staff:
        return redirect_user(user)

    # Account protection
    if not user.is_active or not user.is_approved:

        logout(request)

        messages.error(
            request,
            "Your account is not approved or is inactive."
        )

        return redirect("login")

    context = {
        "current_user": user
    }

    return render(
        request,
        "dashboard/index.html",
        context
    )


# ==========================================
# USER LOGOUT
# ==========================================

@require_POST
@login_required(login_url="login")
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")

# ==========================================
# HOME PAGE REDIRECT
# ==========================================

def home_view(request):

    if request.user.is_authenticated:
        return redirect_user(request.user)

    return redirect("login")