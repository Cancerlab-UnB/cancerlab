# apps/accounts/admin.py
from django.contrib import admin
from .models import InternalUser, PasswordResetToken


@admin.register(InternalUser)
class InternalUserAdmin(admin.ModelAdmin):
    list_display = ("cpf", "nome", "email", "perfil")
    list_filter = ("perfil",)
    search_fields = ("cpf", "nome", "email")
    ordering = ("nome",)


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "expires_at", "used")
    list_filter = ("used",)
