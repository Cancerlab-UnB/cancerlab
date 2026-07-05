# apps/accounts/models.py
#
# Modelos mapeados EXATAMENTE para as tabelas já existentes no banco Railway
# criadas pelo app Streamlit. Por isso usam managed=False e db_column para
# casar com os nomes reais das colunas (ex.: "CPF", "senha").
import bcrypt
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db import models
from django.utils import timezone


class InternalUserManager(BaseUserManager):
    def create_user(self, cpf, nome, email, senha, perfil="aluno", **extra):
        cpf = "".join(filter(str.isdigit, str(cpf)))
        if not cpf:
            raise ValueError("CPF é obrigatório")
        hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
        user = self.model(cpf=cpf, nome=nome, email=email, perfil=perfil, **extra)
        user.password = hashed
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, nome, email, senha, **extra):
        extra.setdefault("perfil", "admin")
        return self.create_user(cpf, nome, email, senha, **extra)


class InternalUser(AbstractBaseUser, PermissionsMixin):
    """
    Usuário interno do laboratório (tabela `usuarios` do banco Streamlit).

    Colunas reais no Railway: id, CPF, nome, email, senha, perfil.
    A senha é armazenada com bcrypt na coluna `senha` — mapeamos o campo
    `password` do Django (AbstractBaseUser) para essa coluna via db_column.
    """

    cpf = models.CharField("CPF", max_length=14, unique=True, db_column="CPF")
    nome = models.CharField("Nome completo", max_length=200, db_column="nome")
    email = models.EmailField("E-mail", db_column="email")
    # AbstractBaseUser já define `password`; só apontamos para a coluna `senha`.
    password = models.CharField("Senha", max_length=255, db_column="senha")
    perfil = models.CharField(
        "Perfil", max_length=30,
        choices=[("aluno", "Aluno"), ("servidor", "Servidor"), ("admin", "Admin")],
        default="aluno", db_column="perfil",
    )
    last_login = None
    USERNAME_FIELD = "cpf"
    REQUIRED_FIELDS = ["nome", "email"]

    objects = InternalUserManager()

    class Meta:
        db_table = "usuarios"
        managed = getattr(settings, 'DB_MANAGED', False)          # tabela já existe no Railway (não migrar)
        verbose_name = "Usuário Interno"
        verbose_name_plural = "Usuários Internos"

    def __str__(self):
        return f"{self.nome} ({self.cpf})"

    # ----- flags de permissão (a tabela não tem essas colunas) -----
    @property
    def is_active(self):
        return True

    @property
    def is_staff(self):
        return str(self.perfil).lower() == "admin"

    @property
    def is_superuser(self):
        return str(self.perfil).lower() == "admin"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    # ----- senha bcrypt (compatível com o hash do Streamlit) -----
    def check_bcrypt_password(self, raw_password: str) -> bool:
        try:
            return bcrypt.checkpw(raw_password.encode(), self.password.encode())
        except Exception:
            return False

    def set_bcrypt_password(self, raw_password: str):
        self.password = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

    # Django chama set_password/check_password internamente em alguns fluxos.
    def set_password(self, raw_password: str):
        self.set_bcrypt_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return self.check_bcrypt_password(raw_password)


class PasswordResetToken(models.Model):
    """Tabela `password_reset_tokens` do banco Streamlit."""
    # user_id inteiro simples (a tabela guarda apenas o id, sem FK forte)
    user = models.ForeignKey(
        InternalUser, on_delete=models.DO_NOTHING,
        db_column="user_id", related_name="reset_tokens",
    )
    token = models.CharField(max_length=255, unique=True, db_column="token")
    expires_at = models.DateTimeField(db_column="expires_at")
    used = models.IntegerField(default=0, db_column="used")

    class Meta:
        db_table = "password_reset_tokens"
        managed = getattr(settings, 'DB_MANAGED', False)
        verbose_name = "Token de Reset de Senha"

    def __str__(self):
        return f"Token para {self.user_id} (usado={self.used})"

    @property
    def is_valid(self):
        return not bool(self.used) and self.expires_at > timezone.now()
