# apps/public/urls.py
from django.urls import path
from . import views

app_name = "public"

urlpatterns = [
    path("",               views.home,         name="home"),
    path("research/",      views.research,     name="research"),
    path("publications/",  views.publications, name="publications"),
    path("people/",        views.people,       name="people"),
    path("partners/",      views.partners,     name="partners"),
    path("positions/",     views.positions,    name="positions"),
    path("equipment/",     views.equipment,    name="equipment"),
    path("news/",          views.news,         name="news"),
]
