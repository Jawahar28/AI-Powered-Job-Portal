from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application

        feilds = [
            "applicant_name",
            "applicant_email",
            "resume",
            "cover_letter",
        ]