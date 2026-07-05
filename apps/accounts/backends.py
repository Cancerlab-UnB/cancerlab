# apps/accounts/backends.py
from django.contrib.auth.backends import BaseBackend
from .models import InternalUser


class CPFBackend(BaseBackend):
    """Autentica usuário interno usando CPF + senha bcrypt."""

    def authenticate(self, request, cpf=None, password=None, **kwargs):
        if not cpf or not password:
            return None
        cpf_limpo = "".join(filter(str.isdigit, str(cpf)))
        try:
            user = InternalUser.objects.get(cpf=cpf_limpo)
        except InternalUser.DoesNotExist:
            return None
        if user.check_bcrypt_password(password) and user.is_active:
            return user
        return None

    def get_user(self, user_id):
        try:
            return InternalUser.objects.get(pk=user_id)
        except InternalUser.DoesNotExist:
            return None
