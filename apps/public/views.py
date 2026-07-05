# apps/public/views.py
import re
from collections import defaultdict, OrderedDict
from datetime import datetime
from html import escape
from urllib.parse import urlparse

from django.shortcuts import render

from .data import (
    ALUMINI, FUNDING_LINKS, NEWS_ITEMS, PARTNERS, PATENTS,
    PEOPLE, PUBLICATIONS, SCHEDULABLE_EQUIPMENT,
)

# ─── Equipment list (informational) — EXATAMENTE como no app Streamlit ───────

EQUIPMENT_LIST = [
    {"name": "Capela de Fluxo Laminar NB2", "url": "https://pnipe.mcti.gov.br/equipment/10574",
     "function": "Class II laminar-flow biosafety cabinet for aseptic sample handling."},
    {"name": "Countless 3", "url": "https://pnipe.mcti.gov.br/equipment/59150",
     "function": "Automated cell counter for rapid cell concentration and viability."},
    {"name": "Centrífuga de bancada", "url": "https://pnipe.mcti.gov.br/equipment/10578",
     "function": "Routine bench centrifugation of tubes and microplates."},
    {"name": "digital PCR", "url": "https://pnipe.mcti.gov.br/equipment/59231",
     "function": "Absolute nucleic-acid quantification by partitioned PCR."},
    {"name": "DNA Workstation", "url": "https://pnipe.mcti.gov.br/equipment/10570",
     "function": "Clean workstation dedicated to DNA/PCR setup to prevent contamination."},
    {"name": "Fluorímetro Qubit 3", "url": "https://pnipe.mcti.gov.br/equipment/59230",
     "function": "Sensitive fluorometric quantification of DNA, RNA, and protein."},
    {"name": "Incubadora de Células com CO₂ (PHP)", "url": "https://pnipe.mcti.gov.br/equipment/59148",
     "function": "CO₂ incubator for controlled-temperature, humidified cell culture."},
    {"name": "Incubadora de Células com CO₂ (Sanyo)", "url": "https://pnipe.mcti.gov.br/equipment/10575",
     "function": "CO₂ incubator for mammalian cell growth under stable conditions."},
    {"name": "Incubadora Shaker", "url": "https://pnipe.mcti.gov.br/equipment/10576",
     "function": "Temperature-controlled orbital shaking for cultures and reactions."},
    {"name": "Ion Chef", "url": "https://pnipe.mcti.gov.br/equipment/10565",
     "function": "Automated template preparation and chip loading for Ion Torrent NGS."},
    {"name": "NanoDrop Plus", "url": "https://pnipe.mcti.gov.br/equipment/59149",
     "function": "Micro-volume UV-Vis spectrophotometer for nucleic acids and protein."},
    {"name": "NanoVue – Espectrofotômetro DNA", "url": "https://pnipe.mcti.gov.br/equipment/10572",
     "function": "Micro-volume spectrophotometry for DNA/RNA quantification."},
    {"name": "Pala Cell Sorter and Single Cell Dispenser", "url": "https://pnipe.mcti.gov.br/equipment/59229",
     "function": "Sorting and dispensing of single cells into plates for downstream assays."},
    {"name": "QuantStudio 3D – PCR Digital", "url": "https://pnipe.mcti.gov.br/equipment/10564",
     "function": "Chip-based digital PCR for precise copy-number and rare variant detection."},
    {"name": "SeptOne Plus – Real-Time PCR", "url": "https://pnipe.mcti.gov.br/equipment/10568",
     "function": "qPCR amplification with real-time fluorescence detection."},
    {"name": "Sequenciador NGS – Ion S5 Plus", "url": "https://pnipe.mcti.gov.br/equipment/10563",
     "function": "Next-generation sequencing for targeted panels and small genomes."},
    {"name": "Sistema de Eletroforese Automatizado – Experion", "url": "https://pnipe.mcti.gov.br/equipment/10566",
     "function": "Automated electrophoresis for RNA/DNA/protein sizing and quality."},
    {"name": "Tanque de Criopreservação", "url": "https://pnipe.mcti.gov.br/equipment/10579",
     "function": "Liquid-nitrogen storage for long-term cryopreservation."},
    {"name": "TapeStation 4150", "url": "https://pnipe.mcti.gov.br/equipment/17245",
     "function": "Automated electrophoresis for DNA/RNA QC using ScreenTape."},
    {"name": "Termociclador PCR", "url": "https://pnipe.mcti.gov.br/equipment/10571",
     "function": "Conventional thermal cycler for endpoint PCR."},
    {"name": "Transiluminador UV", "url": "https://pnipe.mcti.gov.br/equipment/10577",
     "function": "UV visualization of nucleic acids and gels."},
    {"name": "Ultrafreezer −80 °C", "url": "https://pnipe.mcti.gov.br/equipment/10573",
     "function": "Ultra-low temperature storage of biological samples (−80 °C)."},
]

# ─── Months (English) ────────────────────────────────────────────────────────

MONTHS_EN = ["January","February","March","April","May","June",
             "July","August","September","October","November","December"]


def home(request):
    return render(request, "public/home.html")


def research(request):
    return render(request, "public/research.html")


def publications(request):
    pubs_by_year: dict = defaultdict(list)
    pats_by_year: dict = defaultdict(list)
    for p in PUBLICATIONS:
        pubs_by_year[int(p["year"])].append(p)
    for pt in PATENTS:
        pats_by_year[int(pt["year"])].append(pt)

    years = sorted(set(pubs_by_year.keys()) | set(pats_by_year.keys()), reverse=True)
    sections = []
    for y in years:
        sections.append({
            "year": y,
            "publications": pubs_by_year.get(y, []),
            "patents": pats_by_year.get(y, []),
            "count": len(pubs_by_year.get(y, [])) + len(pats_by_year.get(y, [])),
        })
    return render(request, "public/publications.html", {
        "sections": sections,
        "years": years,
    })


def people(request):
    # Build alumini groups in original order
    order = ["Postdoctoral Fellows", "Ph.D.", "M.Sc.", "PIBIC", ""]
    alumini_groups = OrderedDict()
    for key in order:
        items = [a for a in ALUMINI if (a.get("activity") or "") == key]
        if items:
            alumini_groups[key or "Other"] = items

    return render(request, "public/people.html", {
        "people": PEOPLE,
        "alumini_groups": alumini_groups,
    })


def partners(request):
    funding = [{"file": k, "href": v} for k, v in FUNDING_LINKS.items()]
    partners_list = []
    for p in PARTNERS:
        pp = dict(p)
        pp["initials"] = (pp.get("name") or "")[:2]
        partners_list.append(pp)
    return render(request, "public/partners.html", {
        "partners": partners_list,
        "funding": funding,
    })


def positions(request):
    return render(request, "public/positions.html")


def equipment(request):
    return render(request, "public/equipment.html", {
        "equipment_list": EQUIPMENT_LIST,
    })


def _youtube_id(url: str):
    m = re.search(r"(?:youtube\.com/(?:watch\?v=|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    if m: return m.group(1)
    m = re.search(r"[?&]v=([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None


def _host(url: str) -> str:
    try: return urlparse(url).netloc.replace("www.", "")
    except Exception: return "link"


def news(request):
    enriched = []
    for item in NEWS_ITEMS:
        it = dict(item)
        dt = datetime.fromisoformat(it["date_iso"])
        it["date_fmt"] = f"{MONTHS_EN[dt.month-1]} {dt.day}, {dt.year}"
        it["host"] = _host(it["url"])
        if it["kind"] == "video":
            yt_id = _youtube_id(it["url"])
            it["embed"] = (
                f"https://www.youtube-nocookie.com/embed/{yt_id}?rel=0&modestbranding=1&playsinline=1"
                if yt_id else None
            )
        enriched.append(it)

    press_items = [i for i in enriched if i["kind"] == "press"]
    video_items = [i for i in enriched if i["kind"] == "video"]
    return render(request, "public/news.html", {
        "press_items": press_items,
        "video_items": video_items,
    })
