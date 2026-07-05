# apps/accounts/views.py
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone

from .backends import CPFBackend
from .forms import LoginForm, PasswordResetForm, PasswordResetRequestForm, RegisterForm
from .models import InternalUser, PasswordResetToken


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect("internal:index")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cpf = form.cleaned_data["cpf"]
        password = form.cleaned_data["password"]
        backend = CPFBackend()
        user = backend.authenticate(request, cpf=cpf, password=password)
        if user:
            auth_login(request, user, backend="apps.accounts.backends.CPFBackend")
            return redirect(request.GET.get("next", "internal:index"))
        else:
            messages.error(request, "Invalid CPF or password.")

    return render(request, "accounts/login.html", {"form": form})


# ─────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────

@login_required
def logout_view(request):
    auth_logout(request)
    return redirect("public:home")


# ─────────────────────────────────────────────
# CADASTRO
# ─────────────────────────────────────────────

def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        user = InternalUser(
            cpf=d["cpf"],
            nome=d["nome"].strip(),
            email=d["email"].strip().lower(),
            perfil=d["perfil"],
        )
        user.set_bcrypt_password(d["password"])
        user.save()
        messages.success(request, "Account created successfully! Please sign in.")
        return redirect("accounts:login")

    return render(request, "accounts/register.html", {"form": form})


# ─────────────────────────────────────────────
# ESQUECI MINHA SENHA
# ─────────────────────────────────────────────

def password_reset_request_view(request):
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cpf = form.cleaned_data["cpf"]
        email = form.cleaned_data["email"].strip().lower()
        try:
            user = InternalUser.objects.get(cpf=cpf, email=email)
            token_str = secrets.token_urlsafe(48)
            expires = timezone.now() + timedelta(hours=2)
            PasswordResetToken.objects.create(user=user, token=token_str, expires_at=expires)
            reset_url = f"{settings.APP_BASE_URL}/reset-senha/?token={token_str}"
            send_mail(
                "[CancerLab] Password reset",
                f"Use the link below to reset your password (valid for 2 hours):\n\n{reset_url}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except InternalUser.DoesNotExist:
            pass  # Não revelar se usuário existe
        messages.info(request, "If the CPF and e-mail match an account, you will receive a link shortly.")
        return redirect("accounts:login")

    return render(request, "accounts/password_reset_request.html", {"form": form})


def password_reset_view(request):
    token_str = request.GET.get("token") or request.POST.get("token")
    try:
        token_obj = PasswordResetToken.objects.select_related("user").get(token=token_str)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Invalid or expired link.")
        return redirect("accounts:login")

    if not token_obj.is_valid:
        messages.error(request, "This link has already been used or has expired.")
        return redirect("accounts:login")

    form = PasswordResetForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = token_obj.user
        user.set_bcrypt_password(form.cleaned_data["new_password"])
        user.save()
        token_obj.used = True
        token_obj.save()
        messages.success(request, "Password reset successfully!")
        return redirect("accounts:login")

    return render(request, "accounts/password_reset.html", {"form": form, "token": token_str})
