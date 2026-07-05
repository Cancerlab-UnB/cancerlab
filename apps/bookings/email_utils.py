# apps/bookings/email_utils.py
#
# E-mail notifications for the equipment-booking workflow (external users).
# All user-facing text is in English (the booking portal is English-only).
#
# Recipients:
#   • On a new request  → the requester + the lab inbox (cancerlab@unb.br)
#                         + the admin address, asking to approve/reject.
#   • On a decision      → the requester (approval/rejection) + the lab inbox.
#   • On a cancellation  → the requester + the lab inbox.
import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger("cancerlab.bookings")


def _from_email() -> str:
    return getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@cancerlab.unb.br"


def _lab_email() -> str:
    return getattr(settings, "LAB_EMAIL", "cancerlab@unb.br")


def _admin_email() -> str:
    return getattr(settings, "ADMIN_EMAIL", "")


def _send(to: str, subject: str, body: str) -> tuple[bool, str]:
    """
    Sends a single plain-text e-mail.

    • Works out of the box with the console backend (development).
    • With the SMTP backend, requires SMTP_USER / SMTP_PASS to be configured;
      otherwise it logs a clear warning and reports the reason instead of
      raising, so the booking flow never breaks because of e-mail issues.
    """
    if not to:
        return False, "No recipient."

    backend = str(getattr(settings, "EMAIL_BACKEND", "")).lower()
    is_smtp = "smtp" in backend
    host_user = getattr(settings, "EMAIL_HOST_USER", "")
    host_pass = getattr(settings, "EMAIL_HOST_PASSWORD", "")

    if is_smtp and (not host_user or not host_pass):
        logger.warning(
            "SMTP credentials not configured (SMTP_USER/SMTP_PASS). "
            "E-mail NOT sent to %s | subject: %s", to, subject,
        )
        return False, "SMTP credentials not configured."

    try:
        send_mail(subject, body, _from_email(), [to], fail_silently=False)
        logger.info("E-mail sent to %s | subject: %s", to, subject)
        return True, ""
    except Exception as exc:
        logger.error("Failed to send e-mail to %s: %s", to, exc)
        return False, str(exc)


def send_booking_submitted(booking) -> dict:
    """New request: notify the requester and the lab (approval needed)."""
    bid = booking.pk
    equip = booking.equipment_name
    date_ = str(booking.booking_date)
    time_ = str(booking.booking_time)[:5]
    name = booking.user_name
    email = booking.user_email
    notes = booking.notes or "—"
    base_url = getattr(settings, "APP_BASE_URL", "")

    body_user = (
        f"Dear {name},\n\n"
        f"We have received your equipment booking request. It is now pending "
        f"review by the laboratory team.\n\n"
        f"STATUS: PENDING APPROVAL\n\n"
        f"Booking ID : #{bid}\n"
        f"Equipment  : {equip}\n"
        f"Date       : {date_}\n"
        f"Time       : {time_}\n"
        f"Notes      : {notes}\n\n"
        f"You will receive another e-mail as soon as your request is approved "
        f"or declined.\n\n"
        f"Best regards,\nCancerLab — University of Brasília"
    )
    body_lab = (
        f"NEW BOOKING REQUEST — approval required\n\n"
        f"Booking ID : #{bid}\n"
        f"Equipment  : {equip}\n"
        f"Date       : {date_}\n"
        f"Time       : {time_}\n"
        f"Requester  : {name} <{email}>\n"
        f"Phone      : {booking.user_phone}\n"
        f"FUB        : {booking.user_fub}\n"
        f"Notes      : {notes}\n\n"
        f"Please review this request (approve or reject) in the internal panel:\n"
        f"{base_url}/interno/agendamentos/\n"
    )
    ok_user, err_user = _send(email, f"[CancerLab] Booking request #{bid} received — {equip}", body_user)
    ok_lab, err_lab = _send(_lab_email(), f"[CancerLab] New booking #{bid} awaiting approval — {equip}", body_lab)
    admin = _admin_email()
    if admin and admin != _lab_email():
        _send(admin, f"[CancerLab] New booking #{bid} awaiting approval", body_lab)
    return {"user_sent": ok_user, "user_error": err_user, "lab_sent": ok_lab, "lab_error": err_lab}


def send_booking_decision(booking, decision: str, review_note: str = "") -> dict:
    """Decision: notify the requester (approved → confirmation; rejected)."""
    bid = booking.pk
    equip = booking.equipment_name
    date_ = str(booking.booking_date)
    time_ = str(booking.booking_time)[:5]
    name = booking.user_name
    email = booking.user_email
    is_approved = decision == "approved"
    note_txt = review_note or booking.review_note or "—"

    if is_approved:
        headline = "STATUS: APPROVED — your booking is confirmed"
        action_msg = (
            "Great news! Your equipment booking has been approved and is now "
            "confirmed. You may use the equipment at the scheduled date and time."
        )
    else:
        headline = "STATUS: REJECTED"
        action_msg = (
            "Unfortunately, your booking request was not approved. "
            "For questions, please contact cancerlab@unb.br."
        )

    body_user = (
        f"Dear {name},\n\n"
        f"Your booking request has been reviewed.\n\n"
        f"{headline}\n\n"
        f"{action_msg}\n\n"
        f"Booking ID    : #{bid}\n"
        f"Equipment     : {equip}\n"
        f"Date          : {date_}\n"
        f"Time          : {time_}\n"
        f"Reviewer note : {note_txt}\n\n"
        f"Best regards,\nCancerLab — University of Brasília"
    )
    body_lab = (
        f"Booking #{bid} was {'APPROVED' if is_approved else 'REJECTED'} "
        f"by {booking.reviewed_by}.\n\n"
        f"Equipment : {equip}\nDate : {date_}\nTime : {time_}\n"
        f"User      : {name} <{email}>\nNote : {note_txt}"
    )
    subj = "confirmed" if is_approved else "rejected"
    ok_user, err_user = _send(email, f"[CancerLab] Booking #{bid} {subj} — {equip}", body_user)
    ok_lab, err_lab = _send(_lab_email(), f"[CancerLab] Booking #{bid} {subj}", body_lab)
    return {"user_sent": ok_user, "user_error": err_user, "lab_sent": ok_lab, "lab_error": err_lab}


def send_booking_cancelled(booking, cancelled_by_label: str = "requester") -> dict:
    """Cancellation: notify the requester and the lab; free the slot."""
    bid = booking.pk
    equip = booking.equipment_name
    date_ = str(booking.booking_date)
    time_ = str(booking.booking_time)[:5]
    name = booking.user_name
    email = booking.user_email

    body_user = (
        f"Dear {name},\n\n"
        f"Your booking has been cancelled.\n\n"
        f"Booking ID : #{bid}\nEquipment  : {equip}\nDate       : {date_}\nTime       : {time_}\n\n"
        f"The time slot is now available for other users.\n\n"
        f"Best regards,\nCancerLab — University of Brasília"
    )
    body_lab = (
        f"Booking #{bid} was cancelled by {cancelled_by_label}.\n\n"
        f"Equipment : {equip}\nDate : {date_}\nTime : {time_}\nUser : {name} <{email}>"
    )
    ok_user, err_user = _send(email, f"[CancerLab] Booking #{bid} cancelled — {equip}", body_user)
    ok_lab, err_lab = _send(_lab_email(), f"[CancerLab] Booking #{bid} cancelled", body_lab)
    return {"user_sent": ok_user, "user_error": err_user, "lab_sent": ok_lab, "lab_error": err_lab}
