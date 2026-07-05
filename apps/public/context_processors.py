# apps/public/context_processors.py
from django.urls import resolve, Resolver404

# Exact same order and labels as original PAGES_PUBLIC
NAV_ITEMS = [
    ("public:home",        "home"),
    ("public:research",    "research"),
    ("public:publications","publications"),
    ("public:equipment",   "equipments"),
    ("public:people",      "people"),
    ("public:partners",    "partners"),
    ("public:positions",   "open positions"),
    ("public:news",        "news"),
    ("accounts:login",     "Internal Access"),
]


def navbar_context(request):
    try:
        match = resolve(request.path_info)
        active = f"{match.namespace}:{match.url_name}"
    except Resolver404:
        active = "public:home"

    nav = [
        {"url_name": url_name, "label": label, "active": (url_name == active)}
        for url_name, label in NAV_ITEMS
    ]
    return {"nav_items": nav}
