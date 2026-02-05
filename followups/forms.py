from django import forms
from datetime import date
from .models import FollowUp


class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ['patient_name', 'phone', 'language', 'notes', 'due_date']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit():
            raise forms.ValidationError("Phone must be numeric")
        return phone

    def clean_due_date(self):
        due_date = self.cleaned_data['due_date']
        if due_date < date.today():
            raise forms.ValidationError("Due date cannot be in the past")
        return due_date
