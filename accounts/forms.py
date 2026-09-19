from django import forms
from .models import CandidateProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class RegisterForm(UserCreationForm):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your username",
            }
        )
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email",
            }
        )
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Create a password",
            }
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm your password",
            }
        )
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your username",
                "autocomplete": "username",
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        )
    )

class CandidateProfileForm(forms.ModelForm):

    class Meta:
        model = CandidateProfile

        fields = [
            "profile_picture",
            "phone",
            "location",
            "headline",
            "bio",
            "skills",
            "experience",

            # Career preferences
            "preferred_roles",
            "preferred_locations",
            "preferred_job_type",
            "work_mode",
            "expected_salary",

            "education",
            "github",
            "linkedin",
            "resume",
        ]

        widgets = {

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "headline": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                }
            ),

            "skills": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Python, Django, REST API...",
                }
            ),

            "experience": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Fresher, 1 year, 2 years",
                }
            ),

            "preferred_roles": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Python Developer, Backend Developer, Django Developer",
                }
            ),

            "preferred_locations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Hyderabad, Bangalore, Remote",
                }
            ),

            "preferred_job_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "work_mode": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "expected_salary": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 600000",
                    "min": 0,
                }
            ),

            "education": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "github": forms.URLInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "linkedin": forms.URLInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }
class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
        ]

        widgets = {

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter First Name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Last Name",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Email Address",
                }
            ),

        }