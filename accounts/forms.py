
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
)

from .models import User


# =====================================
# ADMIN USER CREATION FORM
# =====================================

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            "full_name",
            "mobile_number",
            "role",
            "is_approved",
            "is_active",
        )


# =====================================
# ADMIN USER CHANGE FORM
# =====================================

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = "__all__"


# =====================================
# PUBLIC REGISTRATION FORM
# =====================================

class UserRegistrationForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            "full_name",
            "mobile_number",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your full name",
            }),

            "mobile_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter mobile number",
                "maxlength": "10",
                "inputmode": "numeric",
            }),
        }

    def clean_mobile_number(self):

        mobile = self.cleaned_data["mobile_number"]

        if not mobile.isdigit() or len(mobile) != 10:
            raise forms.ValidationError(
                "Enter a valid 10-digit mobile number."
            )

        if User.objects.filter(
            mobile_number=mobile
        ).exists():

            raise forms.ValidationError(
                "This mobile number is already registered."
            )

        return mobile
