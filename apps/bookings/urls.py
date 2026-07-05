# apps/bookings/urls.py
from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    path("",                        views.schedule_portal, name="schedule"),
    path("registrar/",              views.ext_register,    name="ext_register"),
    path("login/",                  views.ext_login,       name="ext_login"),
    path("logout/",                 views.ext_logout,      name="ext_logout"),
    path("reservar/",               views.create_booking,  name="create_booking"),
    path("<int:booking_id>/cancelar/", views.cancel_booking, name="cancel_booking"),
]
