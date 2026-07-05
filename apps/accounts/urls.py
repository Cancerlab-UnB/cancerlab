# apps/accounts/urls.py
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/",               views.login_view,                  name="login"),
    path("logout/",              views.logout_view,                  name="logout"),
    path("criar-conta/",         views.register_view,               name="register"),
    path("esqueci-senha/",       views.password_reset_request_view, name="password_reset_request"),
    path("reset-senha/",         views.password_reset_view,         name="password_reset"),
]
