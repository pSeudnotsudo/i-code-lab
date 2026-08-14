from django import forms

from .models import *


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = [
            "name", "enrollment", "program", "level", "certificate_type",
            "completion_date", "issue_date", "assessment_status",
        ]
        widgets = {
            "completion_date": forms.DateInput(attrs={"type": "date"}),
            "issue_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        program_qs = Program.objects.all()
        if hasattr(Program, "is_active"):
            program_qs = program_qs.filter(is_active=True)
        self.fields["program"].queryset = program_qs

        # Level is optional on the form — it defaults to the programme's
        # own level in Certificate.save() if left blank.
        self.fields["level"].required = False

        self.fields["enrollment"].queryset = Enrollment.objects.order_by("-created_at")[:200]
        self.fields["enrollment"].required = False

        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            css = "form-control"
            field.widget.attrs["class"] = (existing + " " + css).strip()

    def clean(self):
        cleaned = super().clean()
        completion = cleaned.get("completion_date")
        issue = cleaned.get("issue_date")
        if completion and issue and issue < completion:
            self.add_error("issue_date", "Issue date can't be before the completion date.")
        return cleaned