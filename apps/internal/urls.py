# apps/internal/urls.py
from django.urls import path
from . import views

app_name = "internal"

urlpatterns = [
    path("",                              views.index,                  name="index"),
    path("dashboard/",                    views.dashboard,              name="dashboard"),
    path("agendamentos/",                 views.manage_bookings,        name="manage_bookings"),
    path("agendamentos/<int:booking_id>/aprovar/",   views.approve_booking,        name="approve_booking"),
    path("agendamentos/<int:booking_id>/rejeitar/",  views.reject_booking,         name="reject_booking"),
    path("agendamentos/<int:booking_id>/cancelar/",  views.cancel_booking_internal,name="cancel_booking"),
    path("biopsia/",                      views.biopsia,                name="biopsia"),
    path("clinicos/",                     views.clinicos,               name="clinicos"),
]
