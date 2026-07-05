# apps/bookings/admin.py
from django.contrib import admin
from .models import BookingAuditLog, EquipmentBooking, ExternalUser


@admin.register(ExternalUser)
class ExternalUserAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "fub_registration", "created_at")
    search_fields = ("full_name", "email", "fub_registration")


@admin.register(EquipmentBooking)
class EquipmentBookingAdmin(admin.ModelAdmin):
    list_display = ("pk", "equipment_name", "booking_date", "booking_time", "user_name", "status", "created_at")
    list_filter = ("status", "equipment_name")
    search_fields = ("user_name", "user_email", "equipment_name")
    ordering = ("-booking_date",)


@admin.register(BookingAuditLog)
class BookingAuditLogAdmin(admin.ModelAdmin):
    list_display = ("booking", "action", "performed_by", "created_at")
    list_filter = ("action",)
    ordering = ("-created_at",)
