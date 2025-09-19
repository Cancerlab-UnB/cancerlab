# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 18:58:02 2025

@author: victo
"""

import streamlit as st
import pandas as pd
import bcrypt 
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, select
from datetime import datetime, date, timedelta
import os
import secrets
import smtplib
from email.message import EmailMessage
from sqlalchemy import DateTime

# top of file
from pathlib import Path
import base64

def data_uri(relpath: str, mime="image/jpeg") -> str:
    p = Path(__file__).parent / relpath
    with open(p, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"

# ====================== Public Page inicio ======================
PRIMARY_BLUE = "#12069D"   # ajuste de cor 
TEXT_DARK = "#1b1f24"

# slug -> menu central 
PAGES_PUBLIC = [
    ("home", "home"),
    ("research", "research"),
    ("publications", "publications"),
    ("people", "people"),  
    ("partners", "partners"),
    ("login", "Internal Access"),
]


def _get_param(key: str, default=None):
    try:
        params = st.query_params     # Streamlit >= 1.32
        val = params.get(key, default)
        if isinstance(val, (list, tuple)):
            return val[0]
        return val
    except Exception:
        params = st.experimental_get_query_params()  # versões desatualizadas 
        return params.get(key, [default])[0] if params.get(key) else default

def _set_param(**kwargs):
    try:
        st.query_params.update(kwargs)
    except Exception:
        st.experimental_set_query_params(**kwargs)

def render_navbar(active: str = "home"):
    logo_src = data_uri("cancerlablogoinicio.jpg", mime="image/jpeg")
    
    st.markdown(
        f"""
        <style>
          /* ===== Topbar container ===== */
          .topbar {{
            position: sticky; top: 0; z-index: 1000;
            background: {PRIMARY_BLUE};
            background: linear-gradient(180deg, rgba(0,0,0,.05) 0%, rgba(0,0,0,0) 100%), {PRIMARY_BLUE};
            border-bottom: 1px solid rgba(0,0,0,.08);
            backdrop-filter: saturate(140%) blur(8px);
            -webkit-backdrop-filter: saturate(140%) blur(8px);
            box-shadow: 0 6px 18px rgba(2,6,23,.08);
          }}
          .topbar-inner {{
            max-width:1180px; margin:0 auto; padding:10px 16px;
            display:grid; grid-template-columns: 1fr auto 1fr; align-items:center; gap:12px;
          }}

          /* ===== Brand (logo + tiny label) ===== */
          .brand {{ display:flex; align-items:center; gap:12px; min-width:0; }}
          .brand img {{ height:42px; width:auto; display:block; border-radius:6px; }}
          .brand small {{
            color: rgba(255,255,255,.95); line-height:1.15; font-weight:600; font-size:12.5px;
            text-shadow: 0 1px 0 rgba(0,0,0,.05);
          }}

          /* ===== Menu ===== */
          .menu {{ display:flex; gap:18px; align-items:center; justify-content:center; overflow:auto hidden; }}
          .menu::-webkit-scrollbar {{ display:none; }}
          .menu a {{
            position: relative;
            text-decoration:none; color:white; text-transform: lowercase;
            padding:8px 12px; border-radius:10px; font-weight:700; letter-spacing:.2px;
            transition: background .2s ease, color .2s ease;
            white-space:nowrap;
          }}
          .menu a:hover {{ background: rgba(255,255,255,.14); }}
          .menu a:focus-visible {{
            outline: 2px solid rgba(255,255,255,.9);
            outline-offset: 2px;
          }}

          /* Active pill (works if class='active' is set) */
          .menu a.active {{
            background: rgba(255,255,255,.22);
          }}
          .menu a.active::after {{
            content:""; position:absolute; left:12px; right:12px; bottom:6px; height:2px;
            background: rgba(255,255,255,.9); border-radius:2px;
          }}

          /* CSS fallback: highlight link whose href matches ?page={active} */
          .menu a[href="?page={active}"] {{
            background: rgba(255,255,255,.22);
          }}
          .menu a[href="?page={active}"]::after {{
            content:""; position:absolute; left:12px; right:12px; bottom:6px; height:2px;
            background: rgba(255,255,255,.9); border-radius:2px;
          }}

          /* ===== Right-side buttons ===== */
          .icons {{ display:flex; gap:10px; align-items:center; justify-content:flex-end; }}
          .icon-btn {{
            display:inline-flex; align-items:center; justify-content:center;
            background: rgba(255,255,255,.08);
            border:1px solid rgba(255,255,255,.55);
            color:white; border-radius:10px; padding:7px 12px; font-weight:800;
            text-decoration:none; line-height:1;
            transition: background .2s ease, transform .15s ease;
          }}
          .icon-btn:hover {{ background: rgba(255,255,255,.16); transform: translateY(-1px); }}
          .icon-btn:active {{ transform: translateY(0); }}

          /* ===== Small screens ===== */
          @media (max-width:760px) {{
            .topbar-inner {{ grid-template-columns: 1fr; gap:10px; }}
            .brand {{ justify-content: space-between; }}
            .icons {{ justify-content:flex-start; }}
            .brand small {{ display:none; }} /* keep it clean on mobile */
          }}
        </style>

        <div class="topbar">
          <div class="topbar-inner">
            <div class="brand">
              <img src="{logo_src}" alt="CancerLab"/>
              <small>Laboratory of Molecular Pathology of Cancer<br>University of Brasília</small>
            </div>
            <nav class="menu">
              {''.join([f'<a target="_self" class="{{"active" if active==slug else ""}}" href="?page={slug}">{label}</a>' for slug,label in PAGES_PUBLIC])}
            </nav>
            <div class="icons">
              <a class="icon-btn" href="https://www.unb.br/" target="_self">UnB</a>
              <a class="icon-btn" href="https://fs.unb.br/" target="_self">FS UnB</a>
            </div>
          </div>
        </div>
        
        
        """,
        
        unsafe_allow_html=True,
    )



def page_home():
    hero_src = data_uri("hero_lab.jpg", mime="image/jpeg")
    st.markdown(
        f"""
        <style>
          /* layout */
          .wrap {{ max-width:1180px; margin:32px auto; padding:0 16px; }}
          .hero {{ display:grid; grid-template-columns: 1fr; gap: 28px; align-items:center; }}
          @media (min-width:980px) {{
            .hero {{ grid-template-columns: 1.05fr 0.95fr; gap: 34px; }}
          }}

          /* title + subtitle */
          .title {{
            font-size: clamp(28px, 4vw, 48px);
            font-weight: 800;
            color: var(--TEXT_DARK, #0f172a);
            margin: 6px 0 10px;
            line-height: 1.12;
          }}
          /* add a small 'kicker' above the title without changing HTML */
          .title::before {{
            content: "";
            display: block;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: .06em;
            text-transform: uppercase;
            color: var(--primary, #1351d8);
            margin: 0 0 6px 0;
          }}

          .lead {{ color:#374151; line-height:1.75; font-size:17px; max-width:72ch; }}

          /* SUBTITLE (paragraph right after the title) */
          .hero .title + .lead {{
            color: var(--primary, #1351d8);
            font-weight: 700;
            font-size: clamp(18px, 2.1vw, 20px);
            line-height: 1.55;
          }}

          /* ‘Our mission:’ emphasis at the start of the long paragraph */
          .lead b {{ color: var(--TEXT_DARK, #0f172a); }}

          /* divider with brand accent */
          .divider {{
            height:1px;
            background: linear-gradient(90deg, var(--primary, #1351d8) 0%, #e6e8ee 25%, #e6e8ee 100%);
            border:0;
            margin:22px 0 18px;
          }}

          /* links inside text */
          .wrap a {{
            color: var(--primary, #1351d8);
            text-decoration: none;
            border-bottom: 1px dashed rgba(19,81,216,.35);
          }}
          .wrap a:hover {{ text-decoration: underline; }}

          /* image frame */
          .imgframe {{
            border:1px solid #e7e7ef;
            border-radius:14px;
            overflow:hidden;
            background:#ffffff;
            box-shadow: 0 12px 30px rgba(2,6,23,.10);
          }}
        </style>
        <div class="wrap">
          <div class="hero">
            <div>
              <div class="title">CancerLab – Laboratory of Molecular Pathology of Cancer</div>
              <p class="lead">The Cancer Molecular Pathology Laboratory (CancerLab) at the University of Brasília is a research laboratory focused on studying molecular targets (genetic and epigenetic) that drive carcinogenesis, with the aim of developing diagnostic and prognostic strategies for cancer treatment.</p>
              <div class="divider"></div>
              <p class="lead"><b>Our mission:</b>Train highly qualified professionals in innovative techniques of gene editing, genomics, and liquid biopsy, applied to prevention and comprehensive care for oncology patients. We also work on developing cutting-edge products and services, strengthening scientific and technological innovation in health.<br><br>Our research focuses on the study of circulating tumor DNA (ctDNA) for clinical applications in liquid biopsy; on the epigenetic analysis of the impact of methyltransferase enzymes in solid tumors and leukemias; and on developing CRISPR/Cas9 gene-editing methods for selective knockout (KO) in cancer.<br><br>The laboratory brings together researchers with expertise in complementary medical-biological areas—Clinical Pathology, Molecular Biology, Biochemistry, Immunology, and Genetics—in order to channel the knowledge required for high-level research in human carcinogenesis.<br><br>The laboratory is the operational unit of the research groups <a href='http://dgp.cnpq.br/dgp/espelhogrupo/769498'>Patologia Molecular do Câncer</a>, created in 2008, and <a href='http://dgp.cnpq.br/dgp/espelhogrupo/775959'>Desenvolvimento e Aplicações em Biópsia Líquida</a>, created in 2022, which aim to unite University of Brasília researchers interested in molecular-level studies of human carcinogenesis and its clinical applications.<br><br>We plan to expand our collaborations to enable the exchange of students and researchers with centers of excellence in other regions of Brazil and abroad</p>
            </div>
            <div class="imgframe">
              <img src="{hero_src}" style="width:100%; display:block;" alt="UnB"/>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )




def page_research():
    st.markdown("## Research\nThis page is under construction.")
    st.info("biopsialiquida") 

def page_publications():
    import html, urllib.parse, requests
    from functools import lru_cache

    st.markdown(
        """
        <style>
          .pub-wrap { max-width:1180px; margin:22px auto; padding:0 16px; }
          .pub-title   { font-weight:800; font-size:clamp(22px,3vw,30px); margin: 6px 0 16px; }
          .pub-list    { list-style:none; padding:0; margin:0; }
          .pub-item    { background:#fff; border:1px solid #e6e8ee; border-radius:12px; padding:12px 14px; margin:10px 0;
                         display:grid; grid-template-columns: 1fr auto; gap:8px; align-items:start; }
          .pub-meta    { color:#475569; font-size:.92rem; margin-top:2px; }
          .pub-link    { text-decoration:none; color:var(--primary, #1351d8); font-weight:800; }
          .pub-link:hover { text-decoration:underline; }
          .pub-year    { color:#0f172a; font-weight:700; opacity:.8; white-space:nowrap; }
          .doi-badge   { display:inline-block; margin-left:8px; font-size:.78rem; padding:2px 8px; border-radius:999px;
                         border:1px solid #cbd5e1; color:#334155; background:#f8fafc; }
          .pub-note    { color:#64748b; font-size:.9rem; margin:10px 0 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- Add/maintain your publications here (authors, title, journal, year) ---
    # The resolver will search DOI by the title string.
    PUBLICATIONS = [
        # 2025
        {"authors": "Lopes, M. A.; Cordeiro, M. E. R.; Barreto, F. A. T.; Moreno, L. S.; Silva, A. A. M.; Loyola, M. B.; Soares, M. V. A.; Sousa, J. B.; Pittella-Silva, F.",
         "title": "Assessment of cfDNA release dynamics during colorectal cancer surgery",
         "journal": "Oncotarget", "year": 2025},
        {"authors": "Hollanda, C. N.; Gualberto, A. C. M.; Motoyama, A. B.; Pittella-Silva, F.",
         "title": "Advancing Leukemia Management Through Liquid Biopsy: Insights into Biomarkers and Clinical Utility",
         "journal": "Cancers", "year": 2025},

        # 2024
        {"authors": "Olivera Santana, B. L.; De Loyola, M. B.; Gualberto, A. C. M.; Pittella-Silva, F.",
         "title": "Genetic Alterations of SMYD4 in Solid Tumors Using Integrative Multi-Platform Analysis",
         "journal": "International Journal of Molecular Sciences", "year": 2024},
        {"authors": "Gatto, C. C.; Cavalcante, C. de Q. O.; Lima, F. C.; Nascimento, É. C. M.; Martins, J. B. L.; Santana, B. L. O.; Gualberto, A. C. M.; Pittella-Silva, F.",
         "title": "Structural Design, Anticancer Evaluation, and Molecular Docking of Newly Synthesized Ni(II) Complexes with ONS-Donor Dithiocarbazate Ligands",
         "journal": "Molecules", "year": 2024},
        {"authors": "Silva-Carvalho, A. É.; Féliu-Braga, L. D. C.; Bogéa, G. M. R.; de Assis, A. J. B.; Pittella-Silva, F.; Saldanha-Araujo, F.",
         "title": "GLP and G9a histone methyltransferases as potential therapeutic targets for lymphoid neoplasms",
         "journal": "Cancer Cell International", "year": 2024},

        # 2023
        {"authors": "Zhu, Y.; Pittella-Silva, F.; Wang, Y.; Wang, T.; Long, F.",
         "title": "Editorial: Epigenetic Regulation and Therapy Resistance in Cancer",
         "journal": "Frontiers in Pharmacology", "year": 2023},
        {"authors": "Cavalcante, C. de Q. O.; da Mota, T. H. A.; de Oliveira, D. M.; Nascimento, É. C. M.; Martins, J. B. L.; Pittella-Silva, F.; Gatto, C. C.",
         "title": "Dithiocarbazate ligands and their Ni(II) complexes with potential biological activity: Structural, antitumor and molecular docking study",
         "journal": "Frontiers in Molecular Biosciences", "year": 2023},
        {"authors": "Mota, T. H. A.; Carmargo, R.; Biojone, E. R.; Guimarães, A. F. R.; Pittella-Silva, F.; Oliveira, D. M.",
         "title": "The Relevance of Telomerase and Telomere-Associated Proteins in B-Acute Lymphoblastic Leukemia",
         "journal": "Genes", "year": 2023},
        {"authors": "Machado, C. M. L.; Skubal, M.; Haedicke, K.; Silva, F. P.; Stater, E. P.; Silva, T. L. A. O.; Costa, É. T.; Masotti, C.; Otake, A. H.; Andrade, L. N. S.; et al.",
         "title": "Membrane-derived particles shed by PSMA-positive cells function as pro-angiogenic stimuli in tumors",
         "journal": "Journal of Controlled Release", "year": 2023},
        {"authors": "Assis, A. J.; Santana, B.; Gualberto, A. C. M.; Silva, F. P.; Pittella-Silva, F.",
         "title": "Therapeutic applications of CRISPR/Cas9 mediated targeted gene editing in acute lymphoblastic leukemia: current perspectives, future challenges, and clinical implications",
         "journal": "Frontiers in Pharmacology", "year": 2023},

        # 2022
        {"authors": "Pittella-Silva, F.",
         "title": "Targeting DNA Methylation as an Epigenetic Leukocyte Counting Tool",
         "journal": "Clinical Chemistry", "year": 2022},
        {"authors": "Watanabe, K.; Nakamura, T.; Kimura, Y.; Motoya, M.; Kojima, S.; Kuraya, T.; …; Pittella-Silva, F.; Nakamura, Y.; Low, A. S.",
         "title": "Tumor-informed approach improved ctDNA detection rate in resected pancreatic cancer",
         "journal": "International Journal of Molecular Sciences", "year": 2022},

        # 2021
        {"authors": "Silva, F. P.; Kimura, Y.; Low, S.-K.; Nakamura, Y.; Motoya, M.",
         "title": "Amplification of mutant in a patient with advanced metastatic pancreatic adenocarcinoma detected by liquid biopsy: A case report",
         "journal": "Molecular and Clinical Oncology", "year": 2021},

        # 2020
        {"authors": "Pittella-Silva, F.; Chin, Y. M.; Chan, H. T.; Nagayama, S.; Miyauchi, E.; Low, S.-K.; Nakamura, Y.",
         "title": "Plasma or Serum: Which Is Preferable for Mutation Detection in Liquid Biopsy?",
         "journal": "Clinical Chemistry", "year": 2020},
    ]

    # optional: fill in any DOIs you already know here to skip lookup
    DOI_CACHE = {
        # Example: "Frontiers in Molecular Biosciences|Dithiocarbazate ligands and their Ni(II) complexes...":
        # "10.3389/fmolb.2023.1146820",
    }

    def _key(journal: str, title: str) -> str:
        return f"{journal.strip()}|{title.strip()}"

    @lru_cache(maxsize=256)
    def find_doi(title: str, journal: str = "", year: int | None = None) -> str | None:
        # First check manual cache
        k = _key(journal, title)
        if k in DOI_CACHE:
            return DOI_CACHE[k]

        # Crossref search by bibliographic title (robust + fast)
        try:
            params = {
                "query.bibliographic": title,
                "rows": 1,
            }
            if year:
                params["filter"] = f"from-pub-date:{year}-01-01,until-pub-date:{year}-12-31"
            r = requests.get("https://api.crossref.org/works", params=params, timeout=6)
            if r.ok:
                items = r.json().get("message", {}).get("items", [])
                if items:
                    doi = items[0].get("DOI")
                    if isinstance(doi, str) and "/" in doi:
                        return doi
        except Exception:
            return None
        return None

    # ---- RENDER ----
    st.markdown('<div class="pub-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="pub-title">Publications</div>', unsafe_allow_html=True)

    st.markdown('<ul class="pub-list">', unsafe_allow_html=True)
    for p in PUBLICATIONS:
        title = p["title"].strip()
        journal = p["journal"].strip()
        year = p["year"]
        authors = p["authors"].strip()

        doi = find_doi(title, journal, year)
        if doi:
            href = f"https://doi.org/{urllib.parse.quote(doi, safe='/')}"
            badge = f'<span class="doi-badge">DOI</span>'
        else:
            # Graceful fallback – Scholar search for the title
            q = urllib.parse.quote_plus(title + " " + journal)
            href = f"https://scholar.google.com/scholar?q={q}"
            badge = f'<span class="doi-badge" title="DOI not found automatically; opening Scholar">search</span>'

        item_html = f"""
          <li class="pub-item">
            <div>
              <a class="pub-link" href="{href}" target="_blank" rel="noopener">{html.escape(title)}</a>{badge}
              <div class="pub-meta">{html.escape(authors)} &middot; <i>{html.escape(journal)}</i></div>
            </div>
            <div class="pub-year">{year}</div>
          </li>
        """
        st.markdown(item_html, unsafe_allow_html=True)
    st.markdown('</ul>', unsafe_allow_html=True)

    st.markdown(
        '<div class="pub-note">Tip: if any item opens a search instead of the article, paste the DOI into <code>DOI_CACHE</code> to force a direct link.</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)


from pathlib import Path
# ---- helpers (put above page_people) ----
PHOTO_DIRS = [
    Path(__file__).parent / "static" / "people",  # preferred place
    Path(__file__).parent,                        # fallback: same folder as .py
]

def find_photo(stem_or_name: str | None) -> Path | None:
    """Return a Path to the first matching image file found in PHOTO_DIRS.
    Accepts 'pittella', 'pittella.jpg', 'Pittella.jpeg', etc."""
    if not stem_or_name:
        return None

    # normalize input
    stem_or_name = stem_or_name.strip()
    name, ext = os.path.splitext(stem_or_name)

    candidates: list[Path] = []

    def add_variants(base_dir: Path, base: str, extension: str | None):
        # try exact
        if extension:
            candidates.append(base_dir / (base + extension))
            candidates.append(base_dir / (base.lower() + extension.lower()))
            candidates.append(base_dir / (base.capitalize() + extension.lower()))
        else:
            for e in (".jpg", ".jpeg", ".png", ".webp"):
                candidates.append(base_dir / (base + e))
                candidates.append(base_dir / (base.lower() + e))
                candidates.append(base_dir / (base.capitalize() + e))

    # Build candidate list across both directories
    if ext:
        for d in PHOTO_DIRS:
            add_variants(d, name, ext)
    else:
        for d in PHOTO_DIRS:
            add_variants(d, name, None)

    # Return the first that exists
    for c in candidates:
        if c.exists():
            return c
    return None

def page_people():


    # Folder where your photos live. Put files like fabio.jpg here.
    BASE_PHOTO_DIR = Path(__file__).parent / "static" / "people"

    PEOPLE = [
        {"name": "Fábio Pittella Silva, PhD", "role": "Principal Investigator - Labhead",
         "photo": "Pittella.jpeg",
         "bio": "Coordinator of the Cancer Molecular Pathology Laboratory at the University of Brasília. Ph.D. in Molecular Pathology from the Human Genome Center, University of Tokyo (2008); M.Sc. in Medical Sciences from the University of Tokyo (2004); B.Sc. in Pharmacy and Biochemistry (Clinical Analysis) from the Federal University of Juiz de Fora (2001). At the University of Tokyo’s Human Genome Center, identified and described the genes WDRPUH, TIPUH1, and SMYD3—the first methyltransferase implicated in human carcinogenesis. Professor at the University of Brasília (since 2008), supervising master’s, doctoral, and postdoctoral trainees. Associate researcher in liquid biopsy at the Cancer Precision Medicine Center, Japanese Foundation for Cancer Research (JFCR), Tokyo (since 2018). Visiting professor at Memorial Sloan Kettering Cancer Center, New York (2014–2018), working on methyltransferase inhibitors. Expertise in molecular genetics, with focus on epigenetics, protein methyltransferases, liquid biopsy, and molecular targets for cancer diagnosis/therapy. Ad-hoc consultant to DECIT/SCTIE/MS, CNPq, FAPITEC/SE, and FAPDF; co-founder of the innovation company i.rad.Particles",
         "degrees": [
             "B.Sc. in Pharmacy & Biochemistry, Federal University of Juiz de Fora (1995–2001)",
             "Complementary Studies in Medical Sciences, University of Tokyo (2001–2002)",
             "M.Sc. in Medical Sciences, University of Tokyo (2002–2004)",
             "Ph.D. in Molecular Pathology, University of Tokyo (2004–2008)",
             "Advanced Training: Semiconductor Sequencing & Digital PCR in Cancer, Université Paris Descartes – Paris V (2012)",
             "Postdoctoral Research in Molecular Pathology, Memorial Sloan Kettering Cancer Center (2014–2015)"
         ],
         "email": "pittella@unb.br", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/4961976945101495", "orcid": "https://orcid.org/0000-0002-9644-7098"},
        {"name": "Andrea Barretto Motoyama, PhD", "role": "Principal Investigator - Labhead",
         "photo": "andrea.jpg",
         "bio": "Associate Professor IV in the Department of Pharmacy at the University of Brasília. She earned a BSc in Biological Sciences (UnB, 1997) and a PhD in Biochemistry (University of Basel, 2002). Her PhD explored signal-transduction pathways that drive cellular resistance to targeted anticancer drugs such as trastuzumab. She completed postdoctoral training at The Scripps Research Institute (RNA stability) and the Burnham Institute for Medical Research (cell-adhesion proteins and Rho-family GTPases). Her work spans cell biology, biochemistry, molecular biology, oncology, and pharmacology",
         "degrees": ["BSc in Biological Sciences, University of Brasília (1997)",
                     "PhD in Biochemistry, University of Basel (2002)",
                     "Postdoctoral Fellow in RNA Stability, The Scripps Research Institute, La Jolla",
                     "Postdoctoral Fellow in Adhesion Proteins & Rho-family GTPases, Burnham Institute for Medical Research, La Jolla"],
         "email": "andreabm@unb.br", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/6229434599232057", "orcid": "https://orcid.org/0000-0002-9280-2638"},
        {"name": "Ana Cristina Moura Gualberto, PhD", "role": "Postdoctoral Fellows",
         "photo": "anagualberto.jpg", "bio": "BSc and teaching licensure in Biological Sciences from UFJF, followed by an MSc and PhD in Immunology investigating matrix metalloproteinases in breast cancer, including RNAi-based silencing. She completed a postdoc at UFJF on adipose-tissue exosomes in tumor progression and is currently a postdoctoral fellow at the University of Brasília working with CRISPR/Cas9 genome editing in cancer. Her experience includes immune response, breast-cancer animal models, cell culture, molecular biology, confocal microscopy, histology and immunohistochemistry, and functional assays of migration, proliferation, and cell viability.",
         "degrees": ["BSc and Teaching Licensure in Biological Sciences, Federal University of Juiz de Fora (2008–2012)",
                     "MSc in Biological Sciences (Immunology), Federal University of Juiz de Fora — focus on matrix metalloproteinases as markers of breast cancer progression (2013–2015)",
                     "PhD in Biological Sciences (Immunology), Federal University of Juiz de Fora — RNAi silencing of matrix metalloproteinases in breast cancer progression (2015–2019)",
                     "Postdoctoral Fellow, Federal University of Juiz de Fora — adipose tissue exosomes in breast cancer",
                     "Postdoctoral Fellow, University of Brasília, CRISPR/Cas9 genome editing in cancer (current)"], "email": "", "institution": "Federal University of Juiz de Fora",
         "lattes": "http://lattes.cnpq.br/6338541953564765", "orcid": ""},
        {"name": "Luis Janssen Maia, PhD", "role": "Postdoctoral Fellows",
         "photo": "luisJ.jpg", "bio": "Experience in microbiology and molecular biology. Work focuses on high-throughput nucleic-acid sequencing (NGS) using both in-house data and public datasets—to study the diversity and molecular evolution of viruses and bacteria, with applications to molecular studies and liquid biopsy in tumors",
         "degrees": ["BSc in Biological Sciences, University of Brasília",
                     "MSc in Molecular Biology, University of Brasília",
                     "PhD in Molecular Biology, University of Brasília"], "email": "", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/7167611866112740", "orcid": ""},
        
        {"name": "Ekaly Ivoneth Porto Apangha, B.Pharm", "role": "Technical assistance",
         "photo": "ekaly.jpg", "bio": "Pharmacist graduated from the University of Brasília (UnB); Specialist in Cancer Care from the Escola Superior de Ciências da Saúde (ESCS). Experienced in chemotherapy compounding (antineoplastic handling), Clinical Pharmacy, Oncologic Clinical Pharmacy, Hospital Pharmacy, and Community Pharmacy",
         "degrees": ["Specialization – Multiprofessional Residency in Cancer Care, ESCS/FEPECS (2018–2020)",
                     "B.Pharm. (Pharmacy), University of Brasília (2011–2016)"], "email": "ekaly.apangha@unb.br", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/0622839652506358", "orcid": ""},
        
        {"name": "André Araújo de Medeiros Silva, MD", "role": "Coloproctologist & General Surgeon • PhD Student",
         "photo": "Andre.jpg", "bio": "Master’s graduate and current PhD candidate in Medical Sciences at the University of Brasília, focused on the molecular pathology of colorectal cancer. Holds a Biomedicine degree (UniCEUB, 2017) and a specialization in Imaging from Hospital Israelita Albert Einstein (2019). Qualified in clinical analysis, molecular biology, and imaging. Currently works in the Radiology Department (CT unit) at Hospital Sírio-Libanês in Brasília",
         "degrees": ["PhD Candidate in Medical Sciences, University of Brasília (2024–present)",
                     "MSc in Medical Sciences, University of Brasília (2021–2023)",
                     "Medical Residency in Coloproctology, Hospital São Rafael (2008–2010)",
                     "Medical Residency in Videolaparoscopy (R3 General Surgery), Hospital Geral Roberto Santos (2007–2008)",
                     "Medical Residency in General Surgery, Hospital Geral Clériston Andrade (2005–2007)",
                     "MD, Escola Bahiana de Medicina e Saúde Pública (1999–2004)"
                     "PhD Candidate in Medical Sciences (Molecular Pathology of Colorectal Cancer), University of Brasília"], "email": "", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/6330213791982657", "orcid": "https://orcid.org/0000-0002-3691-3739"},
        {"name": "Flávio de Alencar Teles Barreto, MSc", "role": "PhD Student",
         "photo": "Flavio.jpg", "bio": "Master’s graduate and current PhD candidate in Medical Sciences at the University of Brasília, focused on the molecular pathology of colorectal cancer. Holds a Biomedicine degree (UniCEUB, 2017) and a specialization in Imaging from Hospital Israelita Albert Einstein (2019). Qualified in clinical analysis, molecular biology, and imaging. Currently works in the Radiology Department (CT unit) at Hospital Sírio-Libanês in Brasília",
         "degrees": ["BSc in Biomedicine, Centro Universitário de Brasília (2017)",
                     "Postgraduate Specialization in Imaging (Imagenologia), Hospital Israelita Albert Einstein (2019)",
                     "MSc in Medical Sciences (Molecular Pathology of Colorectal Cancer), University of Brasília",
                     "PhD Candidate in Medical Sciences (Molecular Pathology of Colorectal Cancer), University of Brasília"], "email": "flavioalencarbarreto92@gmail.com", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/7778492502300819", "orcid": ""},
        {"name": "Brunna Letícia Oliveira Santana, MSc", "role": "PhD Student",
         "photo": "", "bio": "Biologist with an MSc in Medical Sciences focused on cancer epigenetics, now a PhD candidate at the University of Brasília investigating lysine methyltransferase knockouts to identify molecular and therapeutic biomarkers for acute lymphoblastic leukemia",
         "degrees": ["BSc in Biological Sciences (Bachelor), Universidade Paulista – Brasília (2019)",
                     "MSc in Medical Sciences (Cancer Epigenetics), University of Brasília (2022–2024)",
                     "PhD Candidate in Medical Sciences, University of Brasília — Lysine methyltransferase gene knockouts as potential molecular and therapeutic biomarkers for acute lymphoblastic leukemia"], "email": "brunna.los@hotmail.com", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/5131211187661647", "orcid": "https://orcid.org/0000-0003-4402-8358"},
        {"name": "Matheus de Oliveira Andrade, MD", "role": "Clinical Oncologist • PhD Student",
         "photo": "matheusmd.jpg", "bio": "MD graduated from the University of Brasília (UnB), with an exchange program in Biomedical Sciences at Queen Mary University of London (QMUL). Fellowship in Internal Medicine at HCFMRP-USP and in Medical Oncology at ICESP-FMUSP. Currently, he is a clinical oncologist at Rede Américas in Brasília (Hospital Brasília Lago Sul) and a PhD candidate in Medical Sciences at the University of Brasília, focusing on liquid biopsy in colorectal cancer.",
         "degrees": ["PhD Candidate in Medical Sciences, University of Brasília (2025–present)",
                     "Medical Residency in Medical Oncology, ICESP – FMUSP (2022–2025)",
                     "Medical Residency in Internal Medicine, HCFMRP–USP (2020–2022)",
                     "Exchange/Advanced Training in Biomedical Sciences, Queen Mary University of London (2014–2015)",
                     "MD, University of Brasília (2011–2018)"], "email": "matheusandradeoncologia@gmail.com", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/3451033370311538", "orcid": "https://orcid.org/0000-0001-8922-2715"},
        {"name": "Mayra Veloso Ayrimoraes Soares, MD", "role": "Radiologist • PhD Student",
         "photo": "mayramd.jpg", "bio": "MD graduated from the University of Brasília (UnB, 1999), Physician–radiologist with residency training in Radiology and Diagnostic Imaging at Hospital de Base do Distrito Federal (2001–2003). Supervisor of the Radiology and Diagnostic Imaging Residency Program at the University of Brasília. Radiologist at Hospital Sírio-Libanês (Brasília-DF) and at Exame/DASA-DF. Holds an MBA in Management of Clinics, Hospitals and Health Services (FGV, Brasília) and is currently a PhD candidate in Medical Sciences at the University of Brasília",
         "degrees": ["PhD Candidate in Medical Sciences, University of Brasília (2022–present)",
                     "Medical Residency in Radiology and Diagnostic Imaging (R3 optional year), Hospital de Base do Distrito Federal – HBDF (2003–2004)",
                     "Medical Residency in Radiology and Diagnostic Imaging, Hospital de Base do Distrito Federal – HBDF (2001–2003)",
                     "Lato Sensu Specialization in Medical Residency Preceptorship (SUS), Hospital Sírio-Libanês (2015–2016)",
                     "MD, University of Brasília (1993–1999)"], "email": "mayra.veloso@unb.br", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/4358326060572502", "orcid": "https://orcid.org/0000-0003-0796-5123"},
        
        {"name": "Lara De Souza Moreno, MD", "role": "Radiologist • MSc Student",
         "photo": "lara.jpg", "bio": "Holds a medical degree from the Catholic University of Brasília (2020). Residency in Radiology and Diagnostic Imaging at the University Hospital of Brasília (2025). Master’s in Medical Sciences from the University of Brasília (2024). Internal Medicine fellow at the DFSTAR Radiology Service – Rede D’Or.",
         "degrees": ["Master’s Candidate in Medical Sciences, University of Brasília (2024–present)",
                     "Medical Residency in Radiology and Diagnostic Imaging, University Hospital of Brasília / Ebserh (2022–2025)",
                     "Fellowship in Radiology and Diagnostic Imaging (Internal Medicine), Hospital DF Star – Rede D’Or (2025–present)",
                     "M.D., Catholic University of Brasília (2014–2020)"], "email": "larasmoreno@gmail.com", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/4568437840946460", "orcid": "https://orcid.org/0009-0002-3390-4551"},
       
        {"name": "Mariana Braccialli de Loyola, B.Pharm", "role": "MSc Student",
         "photo": "Mari.jpg", "bio": "Pharmacist from the University of Brasília and current Master’s student in the Graduate Program in Medical Sciences at the University of Brasília. Works at the Cancer Molecular Pathology Laboratory, researching lysine methyltransferases in the context of acute lymphoblastic leukemia development.",
         "degrees": ["Master’s Candidate in Medical Sciences, University of Brasília (2024–present)",
                     "B.Pharm. (Pharmacy), University of Brasília (2017–2023)"], "email": "maribraccialli@gmail.com", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/4480047944308175", "orcid": "https://orcid.org/0000-0002-7816-764X"},
        
        {"name": "Israel James Cutrim de Oliveira Filho, MD", "role": "MSc Student",
         "photo": "israel.jpg", "bio": "MD graduated from the Federal University of Maranhão (UFMA), Pinheiro campus (2022). Former Dentistry student (UFMA; program discontinued in 2016). Worked in urgent and emergency care and served in the Mais Médicos program for two years in Eldorado do Sul, RS (2023–2024). Currently a Radiology and Diagnostic Imaging resident at the University Hospital of Brasília (2025–present).",
         "degrees": ["Medical Residency in Radiology and Diagnostic Imaging, University Hospital of Brasília / Ebserh (2025–present)",
                     "M.D., Federal University of Maranhão (2017–2022)"], "email": "", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/0956170261692464", "orcid": ""},
        
        {"name": "Daniel dos Santos Ramos, B.Pharm", "role": "MSc Student",
         "photo": "daniel.jpg", "bio": "Holds a B.Pharm. from the Euro-American Institute of Education, Science and Technology (2013) and a postgraduate specialization in Forensic Sciences from UniLS. Currently a Master’s student in the Graduate Program in Nanoscience and Nanobiotechnology at the University of Brasília (UnB). Served as a Public Policy and Educational Management Analyst at the Federal District Department of Education (2010–2022). Now works as a pharmacist and Responsible Technical Officer of the Green Nanotechnology Laboratory (NAVE), affiliated with the School of Health Sciences and Technologies at the University of Brasília, Ceilândia campus (FCTS/UnB)",
         "degrees": ["Master’s Candidate in Nanoscience and Nanobiotechnology, University of Brasília (2025–present)",
                     "Specialization in Forensic Sciences, UniLS (2016–2017)",
                     "B.Pharm. (Pharmacy), Euro-American Institute of Education, Science and Technology – EUROAM (2009–2013)"], "email": "daniel.ramos@unb.br", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/4153360465428627", "orcid": ""},
        
        {"name": "Sophia Alves da Costa Pereira", "role": "Undergraduate Student",
         "photo": "sofia1.jpg", "bio": "Bachelor’s student in Pharmacy at the University of Brasília (UnB). Graduated in Pre-Pharmacy – Associate in Science from Kansas City Kansas Community College, USA (2024)",
         "degrees": ["B.Sc. Candidate in Pharmacy, University of Brasília (2019–present)",
                     "Associate in Science – Pre-Pharmacy, Kansas City Kansas Community College (2024)"], "email": "", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/7674938627453757", "orcid": ""},
        
        {"name": "Yasmin Albuquerque", "role": "Undergraduate Student",
         "photo": "yas.jpg", "bio": "Undergraduate student in Biological Sciences (B.Sc.) at the University of Brasília (since 2022). Has experience in Molecular Biology with a focus on diagnostics, including RNA extraction, RT-PCR, and PCR for Plant Virology. Also works in human and medical genetics, specializing in the extraction and purification of circulating free DNA (cfDNA) from liquid biopsy and in the development of an alternative in-house cfDNA extraction and purification kit.",
         "degrees": ["B.Sc. Candidate in Biological Sciences, University of Brasília (2022–present)"], "email": "", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/2305511706458935", "orcid": ""},
        
        {"name": "Sofia Arrais Haidar", "role": "Undergraduate Student",
         "photo": "sofia2.jpg", "bio": "Fourth-year medical student at the University of Brasília (UnB), currently seeking experience and training in healthcare, especially in scientific research. Completed high school in 2020 at Colégio Educacional Sigma. Has academic and clinical practice experience in outpatient care, inpatient wards, and operating rooms, with activities at the University Hospital of Brasília (HUB) and Primary Health Units (SES-DF). Actively participates in regional and national congresses, symposia, and courses, as well as academic leagues: Family and Community Medicine (LAMEF-UnB), Cardiology (LACor-UnB), Surgery (LAC-UnB), Hematology (LAHem-UnB), and Neurology (Neuroliga-UnB)",
         "degrees": ["M.D. student, University of Brasília (2021–present)"], "email": "", "institution": "University of Brasília",
         "lattes": " http://lattes.cnpq.br/2664347077103484", "orcid": ""},
        
        {"name": "Priscila de Medeiros Vergara", "role": "Undergraduate Student",
         "photo": "pri.jpg", "bio": "Pharmacy student at the University of Brasília (UnB) (2022–present). Conducts research in microbiology at the Enzymology Laboratory of UnB, working with microorganism cultivation, DNA extraction, and analysis of experimental results.",
         "degrees": ["B.Sc. student in Pharmacy, University of Brasília (2022–present)"], "email": "", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/9595288580014037", "orcid": ""},
        
        {"name": "Matheus Lopes da Silva", "role": "Undergraduate Student",
         "photo": "mtl.jpg", "bio": "Undergraduate student in Pharmacy at the Faculty of Health Sciences, University of Brasília (FCS-UnB), Brazil. Completed high school at Colégio Alub – Associação Lecionar Unificada de Brasília in 2013. Intermediate English. Currently serves as a teaching assistant in the subject of Sanitary Surveillance Applied to Pharmacy, taught by Prof. Helaine Carneiro Capucho (FCS-UnB) and ormer Organizational President of the junior enterprise Terapêutica Jr. (2024) and active member of the ValueHealthLab – Laboratory of Studies for Improving Quality, Patient Safety, and Value in Health, coordinated by Prof. Helaine Carneiro Capucho.",
         "degrees": ["B.Sc. student in Pharmacy, University of Brasília (2019–present)"], "email": "", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/1126659468006228", "orcid": ""},
    
    
    ]

    st.markdown("""
    <style>
      .people-wrap {max-width:1180px;margin:0 auto;padding:0 16px;}
      .person-name {font-weight:700;font-size:1.05rem;line-height:1.2;}
      .person-role {color:#374151;font-size:0.92rem;margin-top:2px;}
      /* style the st.image inside People */
      .people-wrap [data-testid="stImage"] img {
        width:90px;height:90px;object-fit:cover;border-radius:10px;
        border:1px solid #d1d5db;background:#fff;
      }
      .ph-placeholder {
        width:90px;height:90px;border-radius:10px;border:1px dashed #cbd5e1;
        display:flex;align-items:center;justify-content:center;color:#9ca3af;background:#f8fafc;
      }
      /* remove the gray rails/dividers */
      .people-wrap div[data-testid="stDivider"],
      .people-wrap hr,
      .people-wrap [role="separator"] { display:none !important; height:0 !important; border:0 !important; }
      .people-wrap div[data-testid="stExpander"] { border:none !important; box-shadow:none !important; background:transparent !important; }
      .people-wrap div[data-testid="stExpander"] summary { border:none !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## People")
    st.markdown('<div class="people-wrap">', unsafe_allow_html=True)

    for p in PEOPLE:
        # Row: photo + name/role
        left, right = st.columns([0.18, 0.82], gap="large")
        with left:
            photo = p.get("photo") or ""
            if photo.startswith("http://") or photo.startswith("https://"):
                st.image(photo, width=80)
            else:
                path = (BASE_PHOTO_DIR / photo) if photo else None
                if path and path.exists():
                    st.image(str(path), width=120)
                else:
                    st.markdown('<div class="ph-placeholder">?</div>', unsafe_allow_html=True)

        with right:
            st.markdown(f'<div class="person-name">{p["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="person-role">{p.get("role","")}</div>', unsafe_allow_html=True)
            with st.expander("See more"):
                if p.get("bio"):
                    st.write(p["bio"])
                if p.get("degrees"):
                    st.markdown("**Degrees**")
                    st.write("\n".join([f"- {d}" for d in p["degrees"]]))
                links = []
                if p.get("lattes"):
                    links.append(f"[Lattes]({p['lattes']})")
                if p.get("orcid"):
                    links.append(f"[ORCID]({p['orcid']})")
                if links:
                    st.markdown("**Links:** " + " · ".join(links))
                contact = []
                if p.get("email"):
                    contact.append(f"📧 {p['email']}")
                if p.get("institution"):
                    contact.append(f"🏛️ {p['institution']}")
                if contact:
                    st.markdown("**Contact:** " + " • ".join(contact))

    st.markdown('</div>', unsafe_allow_html=True)


    # --- Lab Allumini (simple list, no spreadsheet) ---
    # Put this just ABOVE: st.markdown('</div>', unsafe_allow_html=True)

    # Style (blue subtitle, compact rows)
    st.markdown("""
    <style>
      .alumini-title { color:#040359 !important; font-weight:800; margin: 20px 0 20px; }
      .alumini-item { margin: 6px 0; }
      .alumini-item a { font-weight:700; text-decoration:none; }
      .alumini-meta { color:#040359; margin-left:8px; }
    </style>
    """, unsafe_allow_html=True)

    # Manually maintained list (no spreadsheet import)
    ALUMINI = [
        # Examples — duplicate/edit as needed
         {"name": "Doralina do Amaral Rabello Ramos", "lattes": "http://lattes.cnpq.br/4636606799429977", "year": "2011", "activity": "Postdoc"},
         {"name": "Vívian D'Afonseca da Silva Ferreira", "lattes": "", "year": "2015", "activity": "Postdoc"},
         {"name": "Athos Silva Oliveira", "lattes": "http://lattes.cnpq.br/5665031794527967", "year": "2023", "activity": "Postdoc"},
         {"name": "Luís Henrique Toshihiro Sakamoto", "lattes": "http://lattes.cnpq.br/9517030460820076", "year": "2014", "activity": "Ph.D."},
         {"name": "João Nunes de Mattos Neto", "lattes": "http://lattes.cnpq.br/8975088486815463", "year": "2015", "activity": "Ph.D."},
         {"name": "Alan Jhones Barbosa de Assis", "lattes": "http://lattes.cnpq.br/4200078779107622", "year": "2023", "activity": ""},
         {"name": "Maria Elvira Ribeiro Cordeiro", "lattes": "http://lattes.cnpq.br/0612406263580867", "year": "2024", "activity": ""},
         {"name": "Mailson Alves Lopes", "lattes": "http://lattes.cnpq.br/1366042871721219", "year": "2024", "activity": "M.Sc."},
         {"name": "Maíra de Azevedo Feitosa Araujo", "lattes": "http://lattes.cnpq.br/4044380416858498", "year": "2009", "activity": "M.Sc."},
         {"name": "Carolina Amaro de Moura", "lattes": "http://lattes.cnpq.br/7936117807018383", "year": "2009", "activity": "M.Sc."},
         {"name": "Martha Silva Estrêla", "lattes": "http://lattes.cnpq.br/2003119441638169", "year": "2014", "activity": "M.Sc."},
         {"name": "Rubens dos Santos Samuel de Almeida", "lattes": "http://buscatextual.cnpq.br/buscatextual/visualizacv.jsp?id=K4465112U8", "year": "2014", "activity": "M.Sc."},
         {"name": "Flavia Zattar Piazera", "lattes": "http://lattes.cnpq.br/2024630817705719", "year": "2015", "activity": "M.Sc."},
         {"name": "Luís Augusto Muniz Telles", "lattes": "http://lattes.cnpq.br/1987858702905034", "year": "2016", "activity": "M.Sc."},
         {"name": "Gabriel Henrique Rodrigues Faria", "lattes": "http://lattes.cnpq.br/9780864252081017", "year": "2024", "activity": ""},
         {"name": "Erika Soares Vidigal", "lattes": "http://lattes.cnpq.br/8655167478334942", "year": "", "activity": "PIBIC"},
         {"name": "Carolina Queiroga de Azevedo", "lattes": "http://lattes.cnpq.br/3864899787247206", "year": "", "activity": "PIBIC"},
         {"name": "Guilherme da Rocha Ferreira", "lattes": "http://lattes.cnpq.br/8590158442391134", "year": "", "activity": "PIBIC"},
         {"name": "Larissa Carvalho Meireles", "lattes": "http://lattes.cnpq.br/0859422500973304", "year": "", "activity": "PIBIC"},
         {"name": "Clara Laís Vieira de Almeida", "lattes": "http://buscatextual.cnpq.br/buscatextual/visualizacv.jsp?id=K4465889J8", "year": "", "activity": "PIBIC"},
         {"name": "José Ranclenisson Lopes Moreira", "lattes": "http://buscatextual.cnpq.br/buscatextual/visualizacv.jsp?id=K4465881H6", "year": "", "activity": "PIBIC"},
         {"name": "Rubens dos Santos Samuel de Almeida", "lattes": "http://buscatextual.cnpq.br/buscatextual/visualizacv.jsp?id=K4465112U8", "year": "", "activity": "PIBIC"},
         {"name": "Nathalia Moraes de Vasconcelos", "lattes": "http://lattes.cnpq.br/3874243004616213", "year": "", "activity": "PIBIC"},
         {"name": "Igor Ribeiro Fernandes", "lattes": "http://lattes.cnpq.br/7452149888725969", "year": "", "activity": "PIBIC"},
         {"name": "Victor Henrique Fragoso de Mendonça Santiago Paula", "lattes": "http://lattes.cnpq.br/7903416721142160", "year": "", "activity": "PIBIC"},
         {"name": "Julia Silva Valerio Diniz", "lattes": "http://lattes.cnpq.br/8609581256832375", "year": "", "activity": "PIBIC"},
         {"name": "Anne Caroline Duarte Moreira", "lattes": "http://buscatextual.cnpq.br/buscatextual/visualizacv.jsp?id=K4465126E4", "year": "", "activity": "PIBIC"},
         {"name": "Mariana Carneiro da Cunha", "lattes": "", "year": "", "activity": "PIBIC"},
         {"name": "Luís Augusto Muniz Telles", "lattes": "http://lattes.cnpq.br/1987858702905034", "year": "", "activity": "PIBIC"},
         {"name": "Brenno Vinícius Martins Henrique", "lattes": "http://buscatextual.cnpq.br/buscatextual/visualizacv.jsp?id=K4465807Y2", "year": "", "activity": "PIBIC"},
         {"name": "Isabel Santos Cardoso", "lattes": "http://lattes.cnpq.br/2615729486438083", "year": "", "activity": "PIBIC"},
         {"name": "Hugo Paceli Souza de Oliveira", "lattes": "http://lattes.cnpq.br/9505651806604331", "year": "", "activity": "PIBIC"},
         {"name": "Adriano Drummond de Abreu Barreto", "lattes": "http://lattes.cnpq.br/7298891467901069", "year": "", "activity": "PIBIC"},
         {"name": "Hugo Paceli Souza de Oliveira", "lattes": "", "year": "", "activity": "PIBIC"}

    ]

    # --- Lab Allumini (responsive 3-column grid) ---
    from html import escape
    
    # Keep your ALUMINI list as-is above this block
    
    st.markdown("""
    <style>
      .alumini-title{ color:#040359 !important; font-weight:800; margin:20px 0 16px; }
      .alumini-grid{ display:grid; grid-template-columns:repeat(3,minmax(220px,1fr)); gap:8px 22px; align-items:start; }
      @media (max-width:1000px){ .alumini-grid{ grid-template-columns:repeat(2,minmax(220px,1fr)); } }
      @media (max-width:640px){ .alumini-grid{ grid-template-columns:1fr; } }
    
      .alumini-card{ padding:4px 0; }
      .alumini-card a{ font-weight:700; text-decoration:none; }
      .alumini-card a:hover{ text-decoration:underline; }
      .alumini-meta{ font-size:13px; color:#040359; opacity:.9; margin-top:2px; }
    </style>
    """, unsafe_allow_html=True)
    
    html_rows = ['<h3 class="alumini-title"></h3>', '<div class="alumini-grid">']
    
    order = ["Postdoc","Ph.D.","M.Sc.","PIBIC",""]
    groups = {k:[a for a in ALUMINI if (a.get("activity") or "") == k] for k in order}
    
    html = ['<h3 class="alumini-title">Lab Allumini</h3>']
    for label, items in groups.items():
        if not items: continue
        section_title = label or "Other"
        html.append(f'<h4 style="margin:14px 0 8px;color:#040359;font-weight:700;">{escape(section_title)}</h4>')
        html.append('<div class="alumini-grid">')
        for a in items:
            name = escape(a["name"])
            lattes = (a.get("lattes") or "").strip()
            link_html = f'<a href="{escape(lattes)}" target="_blank" rel="noopener">{name}</a>' if lattes else name
            year = (a.get("year") or "").strip()
            meta_html = f'<div class="alumini-meta">{escape(year) if year else ""}</div>' if year else ""
            html.append(f'<div class="alumini-card">{link_html}{meta_html}</div>')
        html.append('</div>')
    
    st.markdown("".join(html), unsafe_allow_html=True)

    
    html_rows.append('</div>')
    st.markdown("".join(html_rows), unsafe_allow_html=True)



def page_partners():
    """
    Modern partners grid, similar structure to People page:
    - DATA (PARTNERS)  ->  RENDER (HTML with CSS)
    - Logos in static/partners/
    - Clickable name (website), country badge, short summary
    - Optional 'details' slot for future expansion
    """
    from html import escape
    from pathlib import Path

    BASE_LOGO_DIR = Path(__file__).parent / "static" / "partners"

    # === DATA: edit this list like you do for PEOPLE ===
    PARTNERS = [
        {
            "name": "Green Nanotechnology Laboratory (NaVe)",
            "website": "https://nanotecnologiaverde.complexonano.com/sobre-nos/",
            "logo": "nave.jpg",
            "country": "UnB - Brazil",
            "summary": "NaVe is a multi-user lab at UnB’s Faculty of Health Sciences & Technologies (FCTS, Ceilândia) focused on designing and applying nanomaterials and nanosystems for health, environmental, agronomic, and forensic applications"
        },
        {
            "name": "i.rad.Particles",
            "website": "https://i-rad-particles.com/#home",
            "logo": "rdp.jpg",
            "country": "Brazil",
            "summary": "i.rad.Particles is a deep-tech company advancing energy generation and medical biotechnology. We develop electricity from nuclear waste, siRNA-nanoparticle cancer diagnostics/therapies, and imaging methods that repurpose FDA-approved drugs pushing sustainable tech for energy and healthcare"
        },
        {
            "name": "Laboratory for the Development of Nanostructured Systems",
            "website": "https://www2.ufjf.br/ldnano/",
            "logo": "ldnano.jpg",
            "country": "UFJF - Brazil",
            "summary": "LDNano, at UFJF’s School of Pharmacy, develops nanotechnology-based solutions—especially nanoparticle drug-delivery systems—to modulate pharmacological properties. Supported by CNPq and FAPEMIG"
        },
        {
            "name": "Biometals Lab — Metal Biochemistry, Chemical Biology & Oxidative Stress",
            "website": "https://pnipe.mcti.gov.br/laboratory/23798",
            "logo": "biom.jpg",
            "country": "UFABC - Brazil",
            "summary": "Laboratory dedicated to research in biochemistry and bioinorganic chemistry."
        },
        {
            "name": "Juliano Alexandre Chaker, PhD",
            "website": "http://lattes.cnpq.br/1552453739678173",
            "logo": "jc.jpg",
            "country": "UnB - Brazil",
            "summary": "Associate Professor at UnB (since 2010). Materials Science: nanomaterials synthesis/characterization, hybrid polymers, sol–gel, and quality analysis. B.Sc. (1997) and M.Sc. (2000) in Chemistry, UNESP; cotutelle Ph.D. in Materials Science, Université Paris-Sud (2004); Ph.D. in Chemistry, UNESP (2004)"
        },
        {
            "name": "Joao Batista de Sousa, PhD",
            "website": "http://lattes.cnpq.br/4243642626863754",
            "logo": "jb.jpg",
            "country": "UnB - Brazil",
            "summary": "Professor of Clinical Surgery (UnB) and Head of Coloproctology at HUB (UnB). MD (UFTM), M.Sc./Ph.D. (USP), Habilitation (USP–Ribeirão Preto). Board-certified in General Surgery and Coloproctology. Former UnB Vice-Rector and former General Director of HUB. Focus: colorectal cancer, anorectal surgery, colonoscopy, wound healing, abdominal sepsis, and liquid biopsy/ctDNA"
        },
        {
            "name": "Camila Maria Longo Machado, PhD",
            "website": "http://lattes.cnpq.br/8111320783893639",
            "logo": "cm.jpg",
            "country": "HC-FMUSP - Brazil",
            "summary": "CEO, i.rad.Particles; researcher at ICESP (Translational Oncology). Former PqC-VI at LIM-43 HC-FMUSP; collaborations with Columbia University and MSKCC (Grimm Lab). Focus: molecular imaging (fluorescence, RSOM, micro-PET/SPECT/CT), biomaterials, extracellular vesicles/membrane particles; prostate cancer. Degrees: B.Sc., M.Sc., Ph.D. (UNICAMP); postdocs at USP and MSKCC"
        },
        {
            "name": "Giselle Cerchiaro, PhD",
            "website": "http://lattes.cnpq.br/0764162939581973",
            "logo": "gc.jpg",
            "country": "UFABC - Brazil",
            "summary": "Full Professor (UFABC). Biochemistry of trace metals (Cu/Fe/Zn), copper bioinorganic chemistry, ROS & cell signaling, copper-based therapeutics, neurodegeneration/metal homeostasis, metal-chelation nutraceuticals, oxidative stress, and cell-cycle changes. Degrees: B.Sc. UNICAMP; Ph.D. USP; visiting fellow, Rome Tor Vergata; 2019 visiting researcher in Rome"
        },
        {
            "name": "Sergio Augusto Lopes de Souza, PhD",
            "website": "http://lattes.cnpq.br/6829155093609377",
            "logo": "sa.jpg",
            "country": "UFRJ - Brazil",
            "summary": "Associate Professor & Chair of Radiology (UFRJ); CNPq Productivity Fellow; FAPERJ “Scientist of Our State.” Nuclear Medicine specialist focusing on 99mTc/^131I/^18F-labeled cells and molecules for diagnostics and translational research in oncology, renal transplantation, rheumatology, infectious diseases, and cell therapy; SBMN/SBBN member and SBMN rep to ALASBIMN CE committee"
        },
        {
            "name": "Frederico Pittella Silva, PhD",
            "website": "http://lattes.cnpq.br/1840687382026247",
            "logo": "fp.jpg",
            "country": "UFJF - Brazil",
            "summary": "Associate Professor (UFJF). Ph.D. Bioengineering, The University of Tokyo; postdocs at UTokyo (Medicine) and UFSC (Young Talents in Pharmacy). Works on nanocarriers for cancer (RNAi/small molecules), nanoparticle characterization, polymeric micelles, pharmaceutics/dermal delivery, nanotoxicology, and in vivo studies. 53 papers, 1,962 citations, h-index 20 (Google Scholar)"
        },
        # Adicione mais parceiros...
    ]

    # === CSS: same philosophy as People (wrapper + responsive grid) ===
    st.markdown("""
    <style>
      :root {
        --brand:#040359;
        --ink: var(--TEXT_DARK, #0f172a);
        --muted:#4b5563;
        --line:#e5e7eb;
        --card:#ffffff;
      }
      .partners-wrap{ max-width:1180px; margin:0 auto; padding:0 16px; }
      .partners-title{ font-size:clamp(24px,3.4vw,34px); font-weight:800; color:var(--ink); margin:18px 0 14px; }

      /* Auto-fit grid: fills the row with as many 280px cards as fit */
      .partners-grid{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:18px; }

      .partner-card{
        background:var(--card);
        border:1px solid var(--line);
        border-radius:14px;
        padding:14px;
        display:grid;
        grid-template-columns:64px 1fr;
        gap:12px;
        align-items:start;
        transition:transform .12s ease, box-shadow .12s ease, border-color .12s ease;
      }
      .partner-card:hover{
        transform:translateY(-2px);
        box-shadow:0 8px 18px rgba(2,6,23,.08);
        border-color:#d9dde3;
      }

      .partner-logo{
        width:64px;height:64px;border-radius:12px;object-fit:contain;
        border:1px solid var(--line); background:#fff;
      }
      .partner-logo--ph{
        width:64px;height:64px;border-radius:12px;border:1px solid var(--line);
        display:flex;align-items:center;justify-content:center;font-weight:800;color:#9ca3af;background:#f8fafc;
      }

      .partner-title a{ color:var(--brand); font-weight:800; text-decoration:none; }
      .partner-title a:hover{ text-decoration:underline; }

      .partner-summary{ color:var(--muted); margin-top:4px; line-height:1.45; font-size:.95rem; }
      .partner-badge{ display:inline-block; font-size:.78rem; padding:2px 10px; border-radius:999px;
                       border:1px solid #cbd5e1; margin-top:8px; color:#334155; background:#f8fafc; }

      /* Optional list mode: just switch container class if you want a condensed list later */
      .partners-list .partner-card{ grid-template-columns:48px 1fr; padding:10px; }
      .partners-list .partner-logo, .partners-list .partner-logo--ph{ width:48px; height:48px; border-radius:10px; }
    </style>
    """, unsafe_allow_html=True)

    # === RENDER ===
    from textwrap import dedent  # add here (or at file top)
    
    out = ['<div class="partners-wrap">', '<div class="partners-title">Partners</div>',
           '<div class="partners-grid">']  # change to 'partners-list' if you prefer list mode
    
    for p in PARTNERS:
        name = escape(p.get("name",""))
        website = (p.get("website") or "").strip()
        summary = escape(p.get("summary",""))
        country = escape(p.get("country",""))
        logo = (p.get("logo") or "").strip()
    
        # build logo (reuse your data_uri helper)
        logo_html = ""
        if logo:
            path = BASE_LOGO_DIR / logo
            if path.exists():
                ext = path.suffix.lower()
                mime = "image/png" if ext==".png" else ("image/webp" if ext==".webp" else "image/jpeg")
                src = data_uri(str(Path("static/partners")/logo), mime=mime)
                logo_html = f'<img class="partner-logo" src="{src}" alt="{name} logo"/>'
        if not logo_html:
            initials = "".join([w[0] for w in name.split()[:2]]).upper() or "?"
            logo_html = f'<div class="partner-logo--ph">{initials}</div>'
    
        title_html   = f'<a href="{escape(website)}" target="_blank" rel="noopener">{name}</a>' if website else name
        summary_html = f'<div class="partner-summary">{summary}</div>' if summary else ""
        badge_html   = f'<div class="partner-badge">{country}</div>' if country else ""
    
        card_html = dedent(f"""
        <div class="partner-card">
          {logo_html}
          <div>
            <div class="partner-title">{title_html}</div>
            {summary_html}
            {badge_html}
          </div>
        </div>
        """).strip()
    
        out.append(card_html)
    
    out.append("</div></div>")
    st.markdown("".join(out), unsafe_allow_html=True)




def go_login():
    st.session_state.page = "login"
    st.rerun()
# fim do heading

  

APP_BASE_URL = os.getenv("APP_BASE_URL", "https://cancerlab.up.railway.app")
SMTP_HOST    = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT    = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER    = (os.getenv("SMTP_USER") or "").strip()
SMTP_PASS    = (os.getenv("SMTP_PASS") or "").replace(" ", "").strip()
FROM_EMAIL   = SMTP_USER


# --- Configuração da Página ---
st.set_page_config(page_title="CancerLab", layout="wide")

# --- URL do Banco no Railway (PÚBLICA para uso local no Streamlit) ---
DATABASE_URL = "postgresql://postgres:nDxPchIFBWnEZercIqUuEDwxTZsLNBcL@switchback.proxy.rlwy.net:37511/railway"

# --- Criar engine SQLAlchemy ---
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# --- Definição da Tabela ---
usuarios_table = Table('usuarios', metadata,
    Column('id', Integer, primary_key=True),
    Column('CPF', String, unique=True),
    Column('nome', String),
    Column('email', String),
    Column('senha', String),   # Hash da senha (em string)
    Column('perfil', String)
)
password_reset_tokens = Table('password_reset_tokens', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, nullable=False),
    Column('token', String, unique=True, nullable=False),
    Column('expires_at', DateTime, nullable=False),
    Column('used', Integer, default=0, nullable=False)
)

# --- Criação da Tabela no Banco, se não existir ---
def criar_tabela_usuarios():
    metadata.create_all(engine)

criar_tabela_usuarios()

# --- Salvar um novo usuário ---
def salvar_usuario(usuario):
    try:
        with engine.begin() as conn:  # begin() garante commit automático
            print("Tentando salvar:", usuario)
            conn.execute(usuarios_table.insert().values(**usuario))
            print("Salvou!")
    except Exception as e:
        print("❌ Erro ao salvar usuário:", e)

# --- Carregar todos os usuários ---
def carregar_usuarios():
    with engine.connect() as conn:
        result = conn.execute(select(usuarios_table))
        return [dict(row._mapping) for row in result]
# ta em teste essa porra

def get_user_by_email(email: str):
    with engine.connect() as conn:
        res = conn.execute(select(usuarios_table).where(usuarios_table.c.email == email)).fetchone()
        return dict(res._mapping) if res else None

def create_reset_token(user_id: int, ttl_minutes: int = 60) -> str:
    token = secrets.token_urlsafe(32)
    exp = datetime.now() + timedelta(minutes=ttl_minutes)
    with engine.begin() as conn:
        conn.execute(password_reset_tokens.insert().values(
            user_id=user_id, token=token, expires_at=exp, used=0
        ))
    return token

def validate_reset_token(token: str):
    with engine.connect() as conn:
        q = select(password_reset_tokens).where(password_reset_tokens.c.token == token)
        row = conn.execute(q).fetchone()
        if not row:
            return None
        rec = dict(row._mapping)
        if rec["used"] == 1:
            return None
        if rec["expires_at"] < datetime.now():
            return None
        return rec  # contém user_id, token, etc.

def mark_token_used(token: str):
    with engine.begin() as conn:
        conn.execute(
            password_reset_tokens.update()
            .where(password_reset_tokens.c.token == token)
            .values(used=1)
        )

def update_user_password(user_id: int, new_password: str):
    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    with engine.begin() as conn:
        conn.execute(
            usuarios_table.update()
            .where(usuarios_table.c.id == user_id)
            .values(senha=hashed)
        )

def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    msg = EmailMessage()
    msg["Subject"] = "Recuperação de senha - CancerLab"
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(
        f"Olá!\n\nClique para redefinir sua senha (válido por 60 minutos):\n{reset_url}\n\n"
        "Se não foi você, ignore este e-mail."
    )
    try:
        # 587 + STARTTLS
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as s:
            s.ehlo(); s.starttls(); s.ehlo()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        return True
    except smtplib.SMTPAuthenticationError:
        # fallback 465 + SSL
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
            return True
        except Exception:
            return False
    except Exception:
        return False

# --- Verificar se matrícula já existe ---
def usuario_existe(CPF):
    with engine.connect() as conn:
        result = conn.execute(select(usuarios_table).where(usuarios_table.c.CPF == CPF))
        return result.fetchone() is not None

# --- Autenticar usuário ---
def autentica(CPF, senha):
    with engine.connect() as conn:
        result = conn.execute(select(usuarios_table).where(usuarios_table.c.CPF == CPF))
        user = result.fetchone()
        if user:
            user_dict = dict(user._mapping)
            if bcrypt.checkpw(senha.encode(), user_dict['senha'].encode()):
                return user_dict
    return None

# --- Função auxiliar de data ---
def add_months(data, n):
    mes = data.month - 1 + n
    ano = data.year + mes // 12
    mes = mes % 12 + 1
    dia = min(data.day, [31,
        29 if ano % 4 == 0 and not ano % 100 == 0 or ano % 400 == 0 else 28,
        31,30,31,30,31,31,30,31,30,31][mes-1])
    return date(ano, mes, dia)

INTERVALOS_BXL_MESES = {
    "BxL 3": 6,
    "BxL 4": 12,
    "BxL 5": 18,
    "BxL 6": 24,
    "BxL 7": 30
}




st.markdown("""
<style>
/* ===== Paleta ===== */
:root{
  --bg: #F3F9FB;           /* fundo da página */
  --text: #111827;         /* texto padrão */
  --muted: #1F2A37;        /* rótulos/legendas */
  --primary: #173975;      /* azul institucional */
  --primary-hover: #0A74B7;
  --input-bg: #EDF2F7;     /* fundo dos inputs/select */
  --input-text: #111827;   /* texto digitado */
  --placeholder: #6B7280;  /* placeholder */
  --border: #C5D1DE;       /* borda dos inputs */
  --alert-info-bg: #DBECFA;     /* fundo do st.info */
  --alert-info-text: #0B3E61;   /* texto do st.info */
  --alert-success-bg: #E7F4EA;  /* fundo do st.success */
  --alert-success-text:#064715; /* texto do st.success */
  /* Forçar cor dos headings (títulos) do Streamlit */
    h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    .block-container h1 {
      color: var(--text) !important;   /* usa #111827 */
      text-shadow: none !important;    /* remove qualquer sombra clara */
}

/* ===== Fundo e texto ===== */
body, .stApp { 
  background: var(--bg) !important; 
  color: var(--text) !important; 
}

/* ===== Cabeçalho/título da página ===== */
.header-lab-text{
  color: var(--primary) !important;
  text-shadow: 0 2px 8px rgba(0,0,0,0.10);
}

/* ===== Botões ===== */
.stButton > button {
  background: var(--primary);
  color: white;
  border-radius: 1rem;
  padding: 0.75rem 2rem;
  border: none;
  font-size: 1.05rem;
  transition: .2s;
  margin-top: 0.5rem;
  margin-bottom: 1.5rem;
}
.stButton > button:hover { background: var(--primary-hover); }

/* ===== Inputs de texto/senha ===== */
.stTextInput > div > div > input,
.stPassword   > div > div > input{
  background: var(--input-bg) !important; color: var(--input-text) !important;
  border: 1px solid var(--border); border-radius: .6rem; padding: .55rem .75rem;
}
.stTextInput input::placeholder, .stPassword input::placeholder{
  color: var(--placeholder) !important; opacity: 1 !important;
}

/* ===== Labels/legendas ===== */
label, .stMarkdown, .stCaption, .stRadio, .stSelectbox label, .stTextInput label{
  color: var(--muted) !important;
}

/* ===== Selectbox (BaseWeb) ===== */
div[data-baseweb="select"] > div{
  background: var(--input-bg) !important; color: var(--input-text) !important;
  border: 1px solid var(--border); border-radius: .6rem; min-height: 42px;
}
div[data-baseweb="select"] *{ color: var(--input-text) !important; }
div[data-baseweb="select"] svg{ opacity: .85; }

/* Dropdown de opções do select */
div[role="listbox"]{
  background: #fff !important; border: 1px solid var(--border);
}
div[role="listbox"] *{ color: var(--text) !important; }

/* Estados desabilitados */
.stTextInput input:disabled{ color:#6B7280 !important; }
div[data-baseweb="select"][aria-disabled="true"] > div{
  opacity:.8; border-style: dashed;
}

/* ===== Alertas (success/info/warn/error) com texto legível ===== */
.stAlert{ border: none !important; }
.stAlert div[role="alert"]{ box-shadow:none; }
.stAlert[data-baseweb] { box-shadow:none; }

/* Streamlit 1.3x – alvo genérico do conteúdo do alerta */
div[role="alert"]{
  border-radius: .6rem; padding: .8rem 1rem;
}

/* Sucesso */
div[role="alert"].stAlert-success,
div[role="alert"]:has(.markdown-success){
  background: var(--alert-success-bg) !important; color: var(--alert-success-text) !important;
}

/* Info */
div[role="alert"].stAlert-info,
div[role="alert"]:has(.markdown-info){
  background: var(--alert-info-bg) !important; color: var(--alert-info-text) !important;
}

/* Fallback para o componente de notificação recente */
div[data-testid="stNotificationContent"]{
  background: var(--alert-info-bg) !important; color: var(--alert-info-text) !important;
}
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
  background: var(--primary) !important;
  color: white !important;
  border-radius: 1rem !important;
  padding: 0.75rem 2rem !important;
  border: none !important;
  font-size: 1.05rem !important;
  transition: .2s !important;
  margin-top: 0.5rem !important;
  margin-bottom: 1.5rem !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
  background: var(--primary-hover) !important;
}
/* Força estilos legíveis em TODOS os alerts nativos do Streamlit */
.stAlert, .stAlert > div[role="alert"] {
  box-shadow: none !important;
  border: none !important;
  border-radius: .6rem !important;
  padding: .8rem 1rem !important;
}

/* Info */
.stAlert:has([data-testid="stIconInfo"]),
.stAlert[data-testid="stNotification"] {
  background: var(--alert-info-bg) !important;   /* #DBECFA */
  color: var(--alert-info-text) !important;      /* #0B3E61 */
}

/* Success */
.stAlert:has([data-testid="stIconSuccess"]) {
  background: var(--alert-success-bg) !important;   /* #E7F4EA */
  color: var(--alert-success-text) !important;      /* #064715 */
}

/* Warning */
.stAlert:has([data-testid="stIconWarning"]) {
  background: #FFF7E6 !important;
  color: #7A4D00 !important;
}

/* Error */
.stAlert:has([data-testid="stIconError"]) {
  background: #FDE8E8 !important;
  color: #7F1D1D !important;
}

/* Conteúdo interno do alerta (markdown/texto) */
.stAlert [data-testid="stMarkdownContainer"],
.stAlert p, .stAlert span, .stAlert div {
  color: inherit !important;
}
</style>
""", unsafe_allow_html=True)





# === Top navbar + public routing (executa antes do app interno) ===
active_nav = _get_param("page", "home")
if isinstance(active_nav, (list, tuple)):   # <- defensivo, caso venha lista
    active_nav = active_nav[0]

render_navbar(active_nav)



# --- Public pages short-circuit ONLY when not inside the internal app ---
is_internal = st.session_state.get("usuario_logado") is not None or \
              st.session_state.get("page") in {"index", "biopsia", "clinicos"}

if not is_internal:
    if active_nav == "login":
        st.session_state.page = "login"
    elif active_nav in {"home", "research", "publications", "people", "partners"}:
        {"home": page_home,
         "research": page_research,
         "publications": page_publications,
         "people": page_people,
         "partners": page_partners}[active_nav]()
        st.stop()





if "page" not in st.session_state:
    st.session_state.page = "login"

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# 🔹 ADD – ler query params para deep-link (reset)
try:
    params = st.query_params  # Streamlit >= 1.32
except Exception:
    params = st.experimental_get_query_params()  # fallback

if "page" in params and isinstance(params["page"], (list, tuple)):
    qp_page = params["page"][0]
else:
    qp_page = params.get("page")

if qp_page in {"reset_request", "reset"}:
    st.session_state.page = qp_page

# Guardar token vindo pela URL (se houver)
if "reset_token" not in st.session_state:
    st.session_state.reset_token = None

qp_token = None
if "token" in params and isinstance(params["token"], (list, tuple)):
    qp_token = params["token"][0]
else:
    qp_token = params.get("token")

if qp_token:
    st.session_state.reset_token = qp_token

# ---- PÁGINA DE LOGIN ----
if st.session_state.page == "login":
    st.title("Login")

    # Use a form so the click is atomic (no half-reruns)
    with st.form("login_form"):
        CPF = st.text_input("CPF",placeholder="Digite o CPF sem pontos ou traços")
        senha = st.text_input("Senha",type="password",placeholder="Digite sua senha") 
        submitted = st.form_submit_button("Entrar")

    if submitted:
        try:
            user = autentica(CPF, senha)  # bcrypt check inside
            if user:
                st.session_state.usuario_logado = user
                st.session_state.page = "index"
                _set_param(page="index") 
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")
        except Exception as e:
            st.error(f"Falha ao autenticar: {e}")

    st.markdown(
        """
        <div style="margin-top:-0.5rem;margin-bottom:0.5rem;">
          <a href="?page=reset_request" style="font-size:0.85rem; color:#00385C; text-decoration:none;">
            Esqueci minha senha
          </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    if st.button("Criar conta"):
        st.session_state.page = "criar_conta"
        st.rerun()


# CRIAÇÃO DE CONTA ----
elif st.session_state.page == "criar_conta":
    st.title("Criar nova conta")
    nome = st.text_input("Nome completo")
    CPF = st.text_input("CPF")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    perfil = st.radio("Tipo de usuário", ["aluno", "servidor"])
    if st.button("Registrar"):
        # Verifica duplicidade
        if usuario_existe(CPF):  # Aqui você já tem uma função que busca no banco
            st.error("Matrícula já cadastrada!")
        elif not (nome and CPF and email and senha):
            st.error("Preencha todos os campos!")
        else:
            hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
            usuario = {
                "CPF": CPF,
                "nome": nome,
                "email": email,
                "senha": hashed,
                "perfil": perfil
            }
            salvar_usuario(usuario)  # Salva no banco
            st.success("Conta criada com sucesso! Faça login.")
            st.session_state.page = "login"
            st.rerun()

    if st.button("Voltar para login"):
        st.session_state.page = "login"
        st.rerun()
# 🔹 ADD – PÁGINA: solicitação de reset por e-mail ta em teste
elif st.session_state.page == "reset_request":
    st.title("Recuperar senha")
    email_rec = st.text_input("Informe o seu e-mail cadastrado")
    if st.button("Enviar link de recuperação"):
        if not email_rec:
            st.warning("Informe o e-mail.")
        else:
            user = get_user_by_email(email_rec)
            if not user:
                st.error("Este e-mail não está vinculado a nenhuma conta.")
            else:
                token = create_reset_token(user_id=user["id"], ttl_minutes=60)
                reset_url = f"{APP_BASE_URL}/?page=reset&token={token}"
                ok = send_password_reset_email(email_rec, reset_url)
                if ok:
                    st.success("Link enviado! Veja também a caixa de spam/lixo.")
                else:
                    st.error("Falha ao enviar o e-mail. Verifique SMTP_USER/SMTP_PASS e tente novamente.")

    if st.button("Voltar para login"):
        st.session_state.page = "login"
        st.rerun()
# 🔹 ADD – PÁGINA: formulário de redefinição
elif st.session_state.page == "reset":
    st.title("Definir nova senha")
    token = st.session_state.reset_token

    if not token:
        st.error("Link inválido ou ausente. Solicite novamente a recuperação de senha.")
        if st.button("Voltar para solicitar link"):
            st.session_state.page = "reset_request"
            st.rerun()
    else:
        rec = validate_reset_token(token)
        if not rec:
            st.error("Este link é inválido, já foi utilizado ou expirou.")
            if st.button("Solicitar novo link"):
                st.session_state.page = "reset_request"
                st.rerun()
        else:
            nova = st.text_input("Nova senha", type="password")
            conf = st.text_input("Confirmar nova senha", type="password")
            if st.button("Salvar nova senha"):
                if not nova or not conf:
                    st.warning("Preencha a nova senha e a confirmação.")
                elif nova != conf:
                    st.error("As senhas não conferem.")
                elif len(nova) < 6:
                    st.warning("Use uma senha com pelo menos 6 caracteres.")
                else:
                    update_user_password(rec["user_id"], nova)
                    mark_token_used(token)
                    st.success("Senha alterada com sucesso! Faça login.")
                    # Limpa token em memória
                    st.session_state.reset_token = None
                    if st.button("Ir para o login"):
                        st.session_state.page = "login"
                        st.rerun()

# ---- PÁGINA INICIAL (após login) ----
elif st.session_state.page == "index":
    user = st.session_state.usuario_logado
    st.title(f"Bem-vindo, {user['nome']} ({user['perfil']})")
    st.write(f"Email: {user['email']}")
    st.write("Escolha a planilha que deseja acessar:")

    if st.button("Planilha Biopsia Líquida"):
        st.session_state.page = "biopsia"
        _set_param(page="biopsia")   # keep URL in sync
        st.rerun()
            
    if st.button("Dados Clínicos CCR"):
        st.session_state.page = "clinicos"
        _set_param(page="clinicos")  # keep URL in sync
        st.rerun()
   
        
    st.write("Deseja encerrar a sessão?")
    
    if st.button("Logout"):
            st.session_state.page = "login"
            st.session_state.usuario_logado = None
            st.rerun()
            
elif st.session_state.page == "biopsia":
    st.title("Entrada e Acompanhamento de Pacientes - Biópsia Líquida CCR")

    # Botão para voltar
    if st.button("Voltar para o menu"):
        st.session_state.page = "index"
        st.rerun()

    
    if "df_biopsia" not in st.session_state:
        st.session_state.df_biopsia = pd.read_excel("Entrada e Acompanhamento de Pacientes Biópsia Líquida CCR.xlsx")
    df = st.session_state.df_biopsia

    def df_to_html_table(df):
        return df.to_html(escape=True, index=False)


    df_visu = df.copy()
    colunas_vazias = [col for col in df_visu.columns if df_visu[col].isnull().all() or (df_visu[col] == "").all()]
    df_visu = df_visu.drop(columns=colunas_vazias)
    st.subheader("Tabela de pacientes")
    st.dataframe(df_visu)

    # Botão "Próximas coletas agendadas (30 dias)"
    if st.button("Próximas coletas agendadas (30 dias)"):
        hoje = datetime.now().date()
        daqui_30 = hoje + timedelta (days=31)
        lista_agendados = []
        for idx_linha, row in df.iterrows():
            for col in df.columns:
                if "BxL" in col and isinstance(row[col], str):
                    import re
                    m = re.search(r"(\d{2}/\d{2}/\d{4})", row[col])
                    if m:
                        try:
                            data = datetime.strptime(m.group(1), "%d/%m/%Y").date()
                            if hoje < data <= daqui_30:
                                lista_agendados.append({
                                    "Paciente": row[df.columns[0]],
                                    "BxL": col,
                                    "Data": data.strftime("%d/%m/%Y"),
                                    "Obs": row[col]
                                })
                        except Exception:
                            pass
        if lista_agendados:
            st.markdown("### Próximas coletas agendadas nos próximos 30 dias")
            for ag in lista_agendados:
                st.markdown(
                    f"<div style='background:#DBECFA; color:#0B3E61; padding:10px; "
                    f"margin-bottom:8px; border-radius:8px;'>"
                    f"<b>Paciente:</b> {ag['Paciente']}<br>"
                    f"<b>Coleta:</b> {ag['BxL']}<br>"
                    f"<b>Data:</b> <span style='color:#B00020;font-weight:bold'>{ag['Data']}</span><br>"
                    f"<b>Obs:</b> {ag['Obs']}"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                "<div style='background:#DBECFA; color:#0B3E61; padding:10px; "
                "border-radius:8px; font-weight:500;'>"
                "Nenhuma coleta agendada para os próximos 30 dias."
                "</div>",
                unsafe_allow_html=True
            )


    # Seleção do paciente
    nomes_pacientes = df.iloc[:, 0].tolist()
    paciente_selecionado = st.selectbox('Paciente', nomes_pacientes)
    idx = df[df.iloc[:, 0] == paciente_selecionado].index[0]
    dados_paciente = df.iloc[idx, 1:].to_dict()
    st.write(f"**Nome:** {paciente_selecionado}")
    # Bloco BxL com observação
    bxl_cols = [col for col in df.columns if col.strip().upper().startswith("BXL")]
    st.subheader("Registrar Ação BxL")
    col_bxl = st.selectbox(
        "Selecione a coluna BxL para registrar a ação:",
        bxl_cols,
        key=f"bxlcol_{paciente_selecionado}_{idx}"
    )
    obs_bxl = st.text_input(
        "Observação (opcional)",
        key=f"obs_{paciente_selecionado}_{col_bxl}_{idx}"
    )

    cols_bxl = st.columns([2, 1])
    with cols_bxl[0]:
        if st.button("Registrar data de hoje na BxL selecionada", key=f"bxlbtn_{paciente_selecionado}_{col_bxl}_{idx}"):
            hoje = datetime.now().strftime("%d/%m/%Y")
            texto = f"({hoje})"
            if obs_bxl.strip():
                texto += f" {obs_bxl.strip()}"
            st.session_state.df_biopsia.at[idx, col_bxl] = texto
            st.success(f"Registrado '{texto}' para {paciente_selecionado} em '{col_bxl}'!")
            st.rerun()
    with cols_bxl[1]:
        st.caption("Adicione uma observação opcional junto com o registro da data.")

    # Edição dos dados do paciente (sempre visível)
    st.subheader("Editar dados do paciente")
    novos_dados = {}
    for coluna, valor in dados_paciente.items():
        novos_dados[coluna] = st.text_input(
            coluna,
            value=str(valor),
            key=f"{coluna}_{paciente_selecionado}_{idx}_biopsia"
        )
    if st.button('Salvar alterações', key=f"salvar_{paciente_selecionado}_{idx}"):
            for coluna, valor in novos_dados.items():
                st.session_state.df_biopsia.at[idx, coluna] = valor
    PASTA_TCLE = "tcle_uploads"
    os.makedirs(PASTA_TCLE, exist_ok=True)
    
    # Garante que as colunas existem
    if 'TCLE FOTO' not in df.columns:
        df['TCLE FOTO'] = ""

    tcle_path = df.at[idx, 'TCLE FOTO']
    
    if isinstance(tcle_path, str) and tcle_path:
        if st.session_state.get(f"tentar_novo_tcle_biopsia_{idx}", False):
            st.error("Já existe um TCLE enviado para este paciente. Se quiser substituir, remova o anterior primeiro.")
            if st.button("Cancelar envio de novo TCLE", key=f"cancelar_envio_biopsia_{idx}"):
                st.session_state[f"tentar_novo_tcle_biopsia_{idx}"] = False
        else:
            st.image(tcle_path, width=320, caption="TCLE já enviado anteriormente")
            st.info("Já existe um TCLE enviado para este paciente.")
            if st.button("Tentar enviar novo TCLE", key=f"novo_tcle_biopsia_{idx}"):
                st.session_state[f"tentar_novo_tcle_biopsia_{idx}"] = True
    else:
        if st.button("Enviar foto do TCLE", key=f"btn_tcle_biopsia_{idx}"):
            st.session_state[f"tcle_upload_biopsia_{idx}"] = True
    
        if st.session_state.get(f"tcle_upload_biopsia_{idx}", False):
            tcle_foto = st.file_uploader("Selecione a foto do TCLE", type=["png", "jpg", "jpeg"], key=f"tcle_file_biopsia_{idx}")
            if tcle_foto is not None:
                if st.button("Registrar novo TCLE", key=f"reg_tcle_biopsia_{idx}"):
                    caminho = os.path.join(
                        PASTA_TCLE,
                        f"tcle_{paciente_selecionado}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    )
                    with open(caminho, "wb") as f:
                        f.write(tcle_foto.getbuffer())
                    st.session_state.df_biopsia.at[idx, 'TCLE FOTO'] = caminho
                    st.session_state.df_biopsia.at[idx, 'data TCLE'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    st.success("TCLE registrado com sucesso!")
                    st.session_state[f"tcle_upload_biopsia_{idx}"] = False
                    st.rerun()
                
                

    # --- Automatização BxL também na edição ---
    if novos_dados.get("BxL 2"):
        try:
            data_bxl2 = novos_dados["BxL 2"].strip()
            try:
                data_bxl2_date = datetime.strptime(data_bxl2, "%d/%m/%Y")
            except ValueError:
                data_bxl2_date = datetime.strptime(data_bxl2, "%Y-%m-%d")
            for bxl, meses in INTERVALOS_BXL_MESES.items():
                # Só preenche se estiver vazio!
                if not st.session_state.df_biopsia.at[idx, bxl]:
                    data_prox = add_months(data_bxl2_date, meses)
                    msg = f"<span style='color:red;font-weight:bold'>* {data_prox.strftime('%d/%m/%Y')} agendar coleta</span>"
                    st.session_state.df_biopsia.at[idx, bxl] = msg
        except Exception:
            st.warning("Data BxL 2 inválida! Use dd/mm/aaaa.")
            
        st.success("Dados do paciente atualizados!")
    



    # --- Botão remover paciente ---
    def css_remover_minibutton():
        st.markdown("""
        <style>
        .btn-danger + div button{
            padding:.25rem .6rem; font-size:.8rem; border-radius:6px;
            background:#FFF1F2; color:#7F1D1D; border:1px solid #FECACA;
        }
        .btn-danger + div button:hover{ background:#FFE4E6; }
        </style>
        """, unsafe_allow_html=True)
    
    # def “simples” — mesma lógica de antes (drop no DF em memória)
    def remover_paciente(df_key: str, idx: int):
        """
        df_key: 'df_biopsia' ou 'df_clinicos'
        idx: índice (linha) a remover
        """
        df = st.session_state.get(df_key)
        if df is None:
            st.error(f"DataFrame '{df_key}' não está carregado.")
            return
        st.session_state[df_key] = df.drop(idx).reset_index(drop=True)
        st.success("Paciente removido!")
        st.rerun()
    
    # front-end: mini botão vermelho + confirmação
    def botao_remover_paciente(df_key: str, idx: int, nome_exibicao: str, key_prefix: str = ""):
        """
        Renderiza o botão pequeno 'Remover paciente' com confirmação.
        df_key: 'df_biopsia' ou 'df_clinicos'
        idx: índice da linha selecionada
        nome_exibicao: nome que aparece no aviso
        key_prefix: prefixo opcional para não colidir keys quando houver várias linhas
        """
        css_remover_minibutton()
        flag_key = f"{key_prefix}confirmar_remove_{df_key}_{idx}"
    
        # botão pequeno (usa o seletor .btn-danger para estilizar o próximo botão)
        st.markdown("<span class='btn-danger'></span>", unsafe_allow_html=True)
        if st.button("Remover paciente", key=f"{key_prefix}rm_{df_key}_{idx}"):
            st.session_state[flag_key] = True
    
        # confirmação
        if st.session_state.get(flag_key):
            st.warning(f"Tem certeza que deseja remover **{nome_exibicao}**? Essa ação é irreversível.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🗑️ Confirmar", key=f"{key_prefix}rm_yes_{df_key}_{idx}"):
                    remover_paciente(df_key, idx)
            with c2:
                if st.button("Cancelar", key=f"{key_prefix}rm_no_{df_key}_{idx}"):
                    st.session_state[flag_key] = False
    


    # Adicionar novo paciente
    st.subheader("Adicionar novo paciente")
    with st.form("novo_paciente_form_biopsia"):
        novo_nome = st.text_input("Nome do novo paciente", key="novo_nome_biopsia")
        novos_campos = {}
        for coluna in df.columns[1:]:
            if coluna not in ["TCLE", "TCLE FOTO", "TCLE"]:
                novos_campos[coluna] = st.text_input(coluna, key=f"novo_{coluna}_biopsia")

        novo_tcle_foto = st.file_uploader(
            "Enviar foto do TCLE (obrigatório)", type=['png', 'jpg', 'jpeg'], key="novo_tcle_foto"
        )
        submitted = st.form_submit_button("Adicionar")
    
        novo_tcle_enviado = False
        novo_caminho = ""
        if novo_tcle_foto is not None:
            import os
            from datetime import datetime
            PASTA_TCLE = "tcle_uploads"
            os.makedirs(PASTA_TCLE, exist_ok=True)
            novo_caminho = os.path.join(PASTA_TCLE, f"novo_tcle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            with open(novo_caminho, "wb") as f:
                f.write(novo_tcle_foto.getbuffer())
            novo_tcle_enviado = True
    
        if submitted:
            if not novo_nome:
                st.error("Preencha o nome do paciente!")
            elif not novo_tcle_enviado:
                st.error("É obrigatório enviar o TCLE para cadastrar!")
            else:
                # Automatização BxL
                if novos_campos.get("BxL 2"):
                    try:
                        data_bxl2 = novos_campos["BxL 2"].strip()
                        try:
                            data_bxl2_date = datetime.strptime(data_bxl2, "%d/%m/%Y")
                        except ValueError:
                            data_bxl2_date = datetime.strptime(data_bxl2, "%Y-%m-%d")
                        for bxl, meses in INTERVALOS_BXL_MESES.items():
                            if not novos_campos.get(bxl):
                                data_prox = add_months(data_bxl2_date, meses)
                                msg = f"<span style='color:red;font-weight:bold'>* {data_prox.strftime('%d/%m/%Y')} agendar coleta</span>"
                                novos_campos[bxl] = msg
                    except Exception:
                        st.warning("Data BxL 2 inválida! Use dd/mm/aaaa.")
    
                novos_campos["TCLE FOTO"] = novo_caminho
                novos_campos["TCLE"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                nova_linha = [novo_nome] + [novos_campos[col] for col in df.columns[1:]]
                st.session_state.df_biopsia.loc[len(df)] = nova_linha
                st.success("Novo paciente adicionado!")
                st.rerun()


elif st.session_state.page == "clinicos":
    st.title("Dados Clínicos - Pacientes CCR Biópsia Líquida")
    if st.button("Voltar para o menu"):
        st.session_state.page = "index"
        st.rerun()

    # Carrega a nova planilha, se ainda não estiver carregada
    if "df_clinicos" not in st.session_state:
        st.session_state.df_clinicos = pd.read_excel("Dados Clínicos Pacientes CCR Biopsia Liquida.xlsx")
    df = st.session_state.df_clinicos

    st.subheader("Tabela de dados clínicos")
    st.dataframe(df)
    # --- CAMPOS PRINCIPAIS: ajuste se os nomes das colunas forem diferentes na sua planilha! ---
    CAMPOS_PRINCIPAIS = ['CBL', 'TCLE', 'prontuário', 'Nome', 'Data de Nasc']

# Seleção do paciente
    nomes_pacientes = df['CBL'].astype(str).tolist()
    paciente_selecionado = st.selectbox('Selecione o paciente', nomes_pacientes)
    idx = df[df['CBL'].astype(str) == paciente_selecionado].index[0]
    dados_paciente = df.loc[idx].to_dict()



    
    st.subheader("Dados do paciente (principais)")
    campos_novos = {}
    
    # Inputs principais
    for campo in CAMPOS_PRINCIPAIS:
        if campo == "TCLE":
            continue
        valor = dados_paciente.get(campo, "")
        campos_novos[campo] = st.text_input(campo, value=str(valor), key=f"{campo}_{idx}")

    # --- REGISTRO TCLE (OBRIGATÓRIO FOTO) ---
    if 'TCLE FOTO' not in df.columns:
        df['TCLE FOTO'] = ""


    PASTA_TCLE = "tcle_uploads"
    os.makedirs(PASTA_TCLE, exist_ok=True)
    
    tcle_path = dados_paciente.get('TCLE FOTO', '')
    
    # Lógica para controlar tentativa de novo envio
    if isinstance(tcle_path, str) and tcle_path:
        # Se o usuário clicou para enviar novo TCLE mesmo já existindo
        if st.session_state.get(f"tentar_novo_tcle_{idx}", False):
            st.error("Já existe um TCLE enviado para este paciente. Se quiser substituir, remova o anterior primeiro.")
            # Botão para voltar para visualização normal
            if st.button("Cancelar envio de novo TCLE", key=f"cancelar_envio_{idx}"):
                st.session_state[f"tentar_novo_tcle_{idx}"] = False
        else:
            st.image(tcle_path, width=320, caption="TCLE já enviado anteriormente")
            st.info("Já existe um TCLE enviado para este paciente.")
            if st.button("Tentar enviar novo TCLE", key=f"novo_tcle_{idx}"):
                st.session_state[f"tentar_novo_tcle_{idx}"] = True
    else:
        if st.button("Enviar foto do TCLE", key=f"btn_tcle_{idx}"):
            st.session_state[f"tcle_upload_{idx}"] = True
    
        if st.session_state.get(f"tcle_upload_{idx}", False):
            tcle_foto = st.file_uploader("Selecione a foto do TCLE", type=["png", "jpg", "jpeg"], key=f"tcle_file_{idx}")
            if tcle_foto is not None:
                if st.button("Registrar novo TCLE", key=f"reg_tcle_{idx}"):
                    caminho = os.path.join(
                        PASTA_TCLE,
                        f"tcle_{paciente_selecionado}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    )
                    with open(caminho, "wb") as f:
                        f.write(tcle_foto.getbuffer())
                    st.session_state.df_clinicos.at[idx, 'TCLE FOTO'] = caminho
                    st.session_state.df_clinicos.at[idx, 'TCLE'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    st.success("TCLE registrado com sucesso!")
                    st.session_state[f"tcle_upload_{idx}"] = False
                    st.rerun()



    

    # --- OUTROS DADOS ---
    st.markdown("#### Outros dados")
    CAMPOS_OCULTAR = set(CAMPOS_PRINCIPAIS + ["TCLE FOTO", "TCLE DATA ENVIO"])
    outros_campos = [col for col in df.columns if col not in CAMPOS_OCULTAR]
    
    campos_escolhidos = st.multiselect(
        "Quais outros dados deseja editar/registrar?", 
        outros_campos,
        key=f"outros_campos_{idx}")
    
    for campo in campos_escolhidos:
        valor = dados_paciente.get(campo, "")
        campos_novos[campo] = st.text_input(campo, value=str(valor), key=f"{campo}_{idx}_extra")
    
    # --- BOTÃO DE SALVAR ---
    if st.button("Salvar alterações do paciente", key=f"salvar_paciente_{idx}"):
            for campo, valor in campos_novos.items():
                st.session_state.df_clinicos.at[idx, campo] = valor
            st.success("Dados do paciente atualizados!")
    
    # --- CADASTRAR NOVO PACIENTE ---
    with st.expander("Cadastrar novo paciente"):
        st.markdown("#### Preencher campos principais")
        novos_campos = {}
        for campo in CAMPOS_PRINCIPAIS:
            if campo == "TCLE":
                continue
            novos_campos[campo] = st.text_input(f"[Novo] {campo}", key=f"novo_{campo}")
    
        novo_tcle_foto = st.file_uploader("Enviar foto do TCLE (obrigatório)", type=['png', 'jpg', 'jpeg'], key="novo_tcle_foto")
        novo_tcle_enviado = False
        novo_caminho = ""
        if novo_tcle_foto is not None:
            os.makedirs(PASTA_TCLE, exist_ok=True)
            novo_caminho = os.path.join(PASTA_TCLE, f"novo_tcle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            with open(novo_caminho, "wb") as f:
                f.write(novo_tcle_foto.getbuffer())
            novo_tcle_enviado = True
    
        st.markdown("#### Outros dados do novo paciente")
        outros_novos = st.multiselect(
            "Quais outros dados deseja registrar?", 
            outros_campos,
            key="novo_outros_campos")
        for campo in outros_novos:
            novos_campos[campo] = st.text_input(f"[Novo] {campo}", key=f"novo_{campo}_extra")
    
        if st.button("Adicionar novo paciente"):
            if not novo_tcle_enviado:
                st.error("É obrigatório enviar o TCLE para cadastrar!")
            else:
                nova_linha = {**novos_campos, "TCLE FOTO": novo_caminho, "TCLE DATA ENVIO": datetime.now().strftime("%d/%m/%Y %H:%M")}
                for col in df.columns:
                    if col not in nova_linha:
                        nova_linha[col] = ""
                st.session_state.df_clinicos.loc[len(df)] = nova_linha
                st.success("Novo paciente cadastrado!")

    








