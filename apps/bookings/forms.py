# apps/bookings/forms.py
from django import forms
from .models import EQUIPMENT_CHOICES, ExternalUser


class ExternalRegisterForm(forms.Form):
    full_name = forms.CharField(label="Full name", max_length=200)
    email = forms.EmailField(label="E-mail")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput())
    phone = forms.CharField(label="Phone", max_length=30)
    fub_registration = forms.CharField(label="FUB / Institution registration", max_length=30)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if ExternalUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This e-mail is already registered.")
        return email

    def clean(self):
        data = super().clean()
        if data.get("password") != data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return data


class ExternalLoginForm(forms.Form):
    email = forms.EmailField(label="E-mail")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


class BookingForm(forms.Form):
    equipment_name = forms.ChoiceField(label="Equipment", choices=EQUIPMENT_CHOICES)
    booking_date = forms.DateField(
        label="Date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    booking_time = forms.TimeField(
        label="Time",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    notes = forms.CharField(
        label="Notes (optional)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
