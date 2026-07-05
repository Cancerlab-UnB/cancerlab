# apps/accounts/forms.py
from django import forms
from .models import InternalUser


class LoginForm(forms.Form):
    cpf = forms.CharField(
        label="CPF",
        max_length=14,
        widget=forms.TextInput(attrs={"placeholder": "Enter your CPF (digits only)", "autocomplete": "username"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter your password", "autocomplete": "current-password"}),
    )

    def clean_cpf(self):
        return "".join(filter(str.isdigit, self.cleaned_data["cpf"]))


class RegisterForm(forms.Form):
    nome = forms.CharField(label="Full name", max_length=200)
    cpf = forms.CharField(label="CPF", max_length=14)
    email = forms.EmailField(label="E-mail")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())
    perfil = forms.ChoiceField(
        label="User type",
        choices=[("aluno", "Student"), ("servidor", "Staff")],
        widget=forms.RadioSelect,
    )

    def clean_cpf(self):
        cpf = "".join(filter(str.isdigit, self.cleaned_data["cpf"]))
        if len(cpf) != 11:
            raise forms.ValidationError("Invalid CPF. Enter all 11 digits.")
        if InternalUser.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError("This CPF is already registered.")
        return cpf


class PasswordResetRequestForm(forms.Form):
    cpf = forms.CharField(label="CPF", max_length=14)
    email = forms.EmailField(label="Registered e-mail")

    def clean_cpf(self):
        return "".join(filter(str.isdigit, self.cleaned_data["cpf"]))


class PasswordResetForm(forms.Form):
    new_password = forms.CharField(label="New password", widget=forms.PasswordInput())
    confirm_password = forms.CharField(label="Confirm new password", widget=forms.PasswordInput())

    def clean(self):
        data = super().clean()
        if data.get("new_password") != data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match.")
        return data
