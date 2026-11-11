from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            "title",
            "student_name",
            "registration_number",
            "description",
            "department",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
