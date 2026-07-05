# apps/bookings/views.py
from datetime import date, datetime

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .email_utils import send_booking_cancelled, send_booking_decision, send_booking_submitted
from .forms import BookingForm, ExternalLoginForm, ExternalRegisterForm
from .models import BookingAuditLog, EquipmentBooking, ExternalUser, SCHEDULABLE_EQUIPMENT

EXTERNAL_SESSION_KEY = "ext_user_id"


def _get_ext_user(request) -> ExternalUser | None:
    uid = request.session.get(EXTERNAL_SESSION_KEY)
    if uid:
        try:
            return ExternalUser.objects.get(pk=uid)
        except ExternalUser.DoesNotExist:
            del request.session[EXTERNAL_SESSION_KEY]
    return None


# ─────────────────────────────────────────────
# PORTAL DE AGENDAMENTO (Página pública)
# ─────────────────────────────────────────────

def schedule_portal(request):
    """Página principal do portal de agendamento para usuários externos."""
    ext_user = _get_ext_user(request)
    view = request.GET.get("view", "login" if not ext_user else "dashboard")

    # Calendário público (sempre disponível).
    # booking_date é STRING 'YYYY-MM-DD' no banco; a comparação lexicográfica
    # com o ISO de hoje é equivalente à comparação de datas.
    today_iso = date.today().isoformat()
    upcoming = list(
        EquipmentBooking.objects.filter(
            status__in=["pending", "approved", "confirmed"],
            booking_date__gte=today_iso,
        ).order_by("booking_date", "booking_time")
    )

    ctx = {
        "ext_user": ext_user,
        "view": view,
        "upcoming": upcoming,
        "equipment_list": SCHEDULABLE_EQUIPMENT,
    }

    if ext_user and view == "dashboard":
        ctx["bookings"] = EquipmentBooking.objects.filter(
            external_user=ext_user
        ).order_by("-created_at")

    return render(request, "bookings/schedule.html", ctx)


# ─────────────────────────────────────────────
# REGISTRO DE USUÁRIO EXTERNO
# ─────────────────────────────────────────────

@require_http_methods(["POST"])
def ext_register(request):
    form = ExternalRegisterForm(request.POST)
    if form.is_valid():
        d = form.cleaned_data
        ext_user = ExternalUser(
            full_name=d["full_name"].strip(),
            email=d["email"],
            phone=d["phone"].strip(),
            fub_registration=d["fub_registration"].strip(),
        )
        ext_user.set_password(d["password"])
        ext_user.save()
        request.session[EXTERNAL_SESSION_KEY] = ext_user.pk
        messages.success(request, "Account created! Welcome to the scheduling portal.")
        return redirect("bookings:schedule")
    # Se formulário inválido, retorna para a página de registro
    return render(request, "bookings/schedule.html", {
        "view": "register",
        "register_form": form,
        "equipment_list": SCHEDULABLE_EQUIPMENT,
    })


# ─────────────────────────────────────────────
# LOGIN / LOGOUT EXTERNO
# ─────────────────────────────────────────────

@require_http_methods(["POST"])
def ext_login(request):
    form = ExternalLoginForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data["email"].strip().lower()
        password = form.cleaned_data["password"]
        try:
            ext_user = ExternalUser.objects.get(email=email)
            if ext_user.check_password(password):
                request.session[EXTERNAL_SESSION_KEY] = ext_user.pk
                return redirect("bookings:schedule")
        except ExternalUser.DoesNotExist:
            pass
    messages.error(request, "Invalid e-mail or password.")
    return redirect("bookings:schedule")


def ext_logout(request):
    request.session.pop(EXTERNAL_SESSION_KEY, None)
    return redirect("bookings:schedule")


# ─────────────────────────────────────────────
# CRIAR RESERVA
# ─────────────────────────────────────────────

@require_http_methods(["POST"])
def create_booking(request):
    ext_user = _get_ext_user(request)
    if not ext_user:
        messages.error(request, "You must be signed in to make a booking.")
        return redirect("bookings:schedule")

    form = BookingForm(request.POST)
    if form.is_valid():
        d = form.cleaned_data
        # booking_date/time são armazenados como STRING no banco (compat. Streamlit)
        date_str = d["booking_date"].isoformat() if hasattr(d["booking_date"], "isoformat") else str(d["booking_date"])
        time_str = d["booking_time"].strftime("%H:%M") if hasattr(d["booking_time"], "strftime") else str(d["booking_time"])[:5]

        # Refinements: no past dates, and stay within lab hours (08:00–14:00).
        if date_str < date.today().isoformat():
            messages.error(request, "You cannot book a date in the past.")
            return redirect("bookings:schedule")
        if not ("08:00" <= time_str <= "14:00"):
            messages.error(request, "Please choose a time within lab hours (08:00–14:00).")
            return redirect("bookings:schedule")

        # Verifica conflito de horário
        conflict = EquipmentBooking.objects.filter(
            equipment_name=d["equipment_name"],
            booking_date=date_str,
            booking_time=time_str,
            status__in=["pending", "approved", "confirmed"],
        ).exists()
        if conflict:
            messages.error(request, "This time slot is already booked. Please choose another.")
            return redirect("bookings:schedule")

        booking = EquipmentBooking.objects.create(
            external_user=ext_user,
            user_name=ext_user.full_name,
            user_email=ext_user.email,
            user_phone=ext_user.phone,
            user_fub=ext_user.fub_registration,
            equipment_name=d["equipment_name"],
            booking_date=date_str,
            booking_time=time_str,
            notes=d.get("notes", ""),
            status="pending",
        )
        BookingAuditLog.objects.create(
            booking=booking,
            action="submitted",
            performed_by=f"user:{ext_user.full_name}",
            note="Booking submitted by external user.",
        )
        send_booking_submitted(booking)
        messages.success(request, f"Booking #{booking.pk} submitted successfully! Awaiting approval.")
    else:
        for field, errs in form.errors.items():
            for e in errs:
                messages.error(request, f"{field}: {e}")

    return redirect("bookings:schedule")


# ─────────────────────────────────────────────
# CANCELAR RESERVA (pelo próprio usuário)
# ─────────────────────────────────────────────

@require_http_methods(["POST"])
def cancel_booking(request, booking_id: int):
    ext_user = _get_ext_user(request)
    if not ext_user:
        messages.error(request, "Access denied.")
        return redirect("bookings:schedule")

    try:
        booking = EquipmentBooking.objects.get(pk=booking_id, external_user=ext_user)
    except EquipmentBooking.DoesNotExist:
        messages.error(request, "Booking not found.")
        return redirect("bookings:schedule")

    if booking.status not in ("pending", "approved", "confirmed"):
        messages.error(request, "This booking cannot be cancelled.")
        return redirect("bookings:schedule")

    booking.status = "cancelled"
    booking.cancelled_by = f"user:{ext_user.full_name}"
    booking.cancelled_at = timezone.now()
    booking.save()

    BookingAuditLog.objects.create(
        booking=booking,
        action="cancelled",
        performed_by=f"user:{ext_user.full_name}",
        note="Cancelled by the external user.",
    )
    send_booking_cancelled(booking, cancelled_by_label=ext_user.full_name)
    messages.success(request, f"Booking #{booking.pk} cancelled.")
    return redirect("bookings:schedule")
