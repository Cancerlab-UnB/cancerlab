# apps/bookings/models.py
#
# Mapeamento EXATO das tabelas de agendamento já existentes no Railway
# (criadas pelo Streamlit). Todas com managed=False.
#
# IMPORTANTE: no banco original, booking_date e booking_time são STRINGS
# ('YYYY-MM-DD' e 'HH:MM'). Mantemos como CharField para compatibilidade total.
import bcrypt
from datetime import datetime
from django.conf import settings
from django.db import models
from django.utils import timezone


class ExternalUser(models.Model):
    """Tabela `external_users` — usuário externo para reserva de equipamentos."""
    full_name = models.CharField("Nome completo", max_length=200, db_column="full_name")
    email = models.EmailField("E-mail", unique=True, db_column="email")
    password_hash = models.CharField("Senha (bcrypt)", max_length=255, db_column="password_hash")
    phone = models.CharField("Telefone", max_length=50, db_column="phone")
    fub_registration = models.CharField("Matrícula FUB", max_length=50, db_column="fub_registration")
    created_at = models.DateTimeField(default=timezone.now, db_column="created_at")

    class Meta:
        db_table = "external_users"
        managed = getattr(settings, 'DB_MANAGED', False)
        verbose_name = "Usuário Externo"
        verbose_name_plural = "Usuários Externos"

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    def set_password(self, raw_password: str):
        self.password_hash = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, raw_password: str) -> bool:
        try:
            return bcrypt.checkpw(raw_password.encode(), self.password_hash.encode())
        except Exception:
            return False


BOOKING_STATUS_CHOICES = [
    ("pending",   "Aguardando Aprovação"),
    ("approved",  "Aprovado"),
    ("rejected",  "Rejeitado"),
    ("cancelled", "Cancelado"),
]

# Lista EXATA de equipamentos agendáveis do app Streamlit.
SCHEDULABLE_EQUIPMENT = [
    "qPCR StepOne Plus",
    "TapeStation",
    "Ion S5 Sequencer",
    "Cell Sorter",
    "DNA Workstation",
]

EQUIPMENT_CHOICES = [(e, e) for e in SCHEDULABLE_EQUIPMENT]


class EquipmentBooking(models.Model):
    """
    Tabela `equipment_bookings` do banco Streamlit.

    booking_date / booking_time são armazenados como STRING no banco original,
    então usamos CharField para não quebrar a compatibilidade.
    """
    # No banco é external_user_id (inteiro simples). Usamos FK com db_column.
    external_user = models.ForeignKey(
        ExternalUser, on_delete=models.DO_NOTHING, null=True,
        db_column="external_user_id", related_name="bookings",
    )
    user_name  = models.CharField("Nome do usuário", max_length=200, db_column="user_name")
    user_email = models.EmailField("E-mail do usuário", db_column="user_email")
    user_phone = models.CharField("Telefone", max_length=50, db_column="user_phone")
    user_fub   = models.CharField("Matrícula FUB", max_length=50, db_column="user_fub")

    equipment_name = models.CharField("Equipamento", max_length=120, db_column="equipment_name")
    booking_date   = models.CharField("Data", max_length=20, db_column="booking_date")   # 'YYYY-MM-DD'
    booking_time   = models.CharField("Horário", max_length=10, db_column="booking_time")  # 'HH:MM'

    status      = models.CharField("Status", max_length=20, default="pending", db_column="status")
    notes       = models.TextField("Observações", blank=True, null=True, db_column="notes")

    reviewed_by  = models.CharField("Revisado por", max_length=200, blank=True, null=True, db_column="reviewed_by")
    reviewed_at  = models.DateTimeField("Data da revisão", null=True, blank=True, db_column="reviewed_at")
    review_note  = models.TextField("Nota da revisão", blank=True, null=True, db_column="review_note")

    cancelled_by = models.CharField("Cancelado por", max_length=200, blank=True, null=True, db_column="cancelled_by")
    cancelled_at = models.DateTimeField("Data do cancelamento", null=True, blank=True, db_column="cancelled_at")

    created_at = models.DateTimeField(default=timezone.now, db_column="created_at")

    class Meta:
        db_table = "equipment_bookings"
        managed = getattr(settings, 'DB_MANAGED', False)
        verbose_name = "Reserva de Equipamento"
        verbose_name_plural = "Reservas de Equipamentos"

    def __str__(self):
        return f"#{self.pk} – {self.equipment_name} em {self.booking_date} por {self.user_name}"

    # ---- Helpers para exibir data/hora formatadas nos templates ----
    @property
    def date_display(self):
        try:
            return datetime.strptime(str(self.booking_date), "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            return self.booking_date

    @property
    def time_display(self):
        return str(self.booking_time)[:5]


class BookingAuditLog(models.Model):
    """Tabela `booking_audit_log` — registro de ações sobre reservas."""
    booking = models.ForeignKey(
        EquipmentBooking, on_delete=models.DO_NOTHING,
        db_column="booking_id", related_name="audit_logs",
    )
    action = models.CharField(max_length=30, db_column="action")
    performed_by = models.CharField(max_length=200, db_column="performed_by")
    note = models.TextField(blank=True, null=True, db_column="note")
    created_at = models.DateTimeField(default=timezone.now, db_column="created_at")

    class Meta:
        db_table = "booking_audit_log"
        managed = getattr(settings, 'DB_MANAGED', False)
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"

    def __str__(self):
        return f"[{self.action}] Reserva #{self.booking_id} por {self.performed_by}"
