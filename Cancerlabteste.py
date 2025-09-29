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
from PIL import Image
# top of file
from pathlib import Path
import base64
ICON_PATH = Path(__file__).parent / "static" / "cancerlab_icon.png"
st.set_page_config(
    page_title="CancerLab – Laboratory of Molecular Pathology of Cancer",
    page_icon=Image.open(ICON_PATH),   # can also pass the path string
    layout="wide"
)

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
    ("positions", "open positions"),   # + add this
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
          :root {{
            --bar-bg: {PRIMARY_BLUE};
            --bar-shadow: 0 6px 18px rgba(2,6,23,.08);
          }}
          /* ===== Remove Streamlit's top gap so the bar sits at the very top ===== */
          header[data-testid="stHeader"] {{ height: 0 !important; }}
          .main .block-container {{ padding-top: 0 !important; }}
          div[data-testid="stDecoration"] {{ display:none; }} /* removes tiny default stripe */
          /* ===== Topbar ===== */
          .topbar {{
            position: sticky; top: 0; left: 0; right: 0; z-index: 1000;
            background: linear-gradient(180deg, rgba(0,0,0,.05) 0%, rgba(0,0,0,0) 100%), var(--bar-bg);
            border-bottom: 1px solid rgba(0,0,0,.08);
            backdrop-filter: saturate(140%) blur(8px);
            -webkit-backdrop-filter: saturate(140%) blur(8px);
            box-shadow: var(--bar-shadow);
            padding-top: max(env(safe-area-inset-top), 0px);
          }}
          .topbar-inner {{
            max-width:1180px; margin:0 auto; padding:10px 16px;
            display:grid; grid-template-columns: auto 1fr auto; align-items:center; gap:16px;
          }}
          /* ===== Brand (logo + clean multiline label) ===== */
          .brand {{ display:flex; align-items:center; gap:12px; min-width:0; }}
          .brand img {{ height:44px; width:auto; display:block; border-radius:8px; }}
          .brand-label {{
            display:grid; grid-auto-rows:min-content;
            max-width: 210px;        /* keeps wrapping consistent */
            line-height:1.15;
            color: rgba(255,255,255,.96);
            text-shadow: 0 1px 0 rgba(0,0,0,.05);
            font-weight:700; font-size:12.5px; letter-spacing:.1px;
          }}
          .brand-label .uofb {{ opacity:.95; font-weight:800; }}
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
          /* Active state */
          .menu a.active, .menu a[href="?page={active}"] {{
            background: rgba(255,255,255,.22);
          }}
          .menu a.active::after, .menu a[href="?page={active}"]::after {{
            content:""; position:absolute; left:12px; right:12px; bottom:6px; height:2px;
            background: rgba(255,255,255,.9); border-radius:2px;
          }}
          /* ===== Right-side quick links ===== */
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
          /* ===== Small screens ===== */
          @media (max-width:760px) {{
            .topbar-inner {{ grid-template-columns: 1fr; gap:10px; }}
            .brand-label {{ display:none; }} /* keep it clean on mobile */
            .menu {{ justify-content:flex-start; }}
          }}
        </style>
        <div class="topbar">
          <div class="topbar-inner">
            <div class="brand">
              <img src="{logo_src}" alt="CancerLab"/>
              <div class="brand-label">
                <span>Laboratory of</span>
                <span>Molecular Pathology of Cancer</span>
                <span class="uofb">University of Brasília</span>
              </div>
            </div>
            <nav class="menu">
              {''.join([f'<a target="_self" class="{{"active" if active==slug else ""}}" href="?page={slug}">{label}</a>' for slug,label in PAGES_PUBLIC])}
            </nav>
            <div class="icons">
              <a class="icon-btn" href="https://www.unb.br/" target="_self">UnB</a>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def page_home():
    # unchanged assets
    hero_src = data_uri("hero_lab.jpg", mime="image/jpeg")
    left_img = data_uri("imghome1.jpg", mime="image/jpeg")
    right_img = data_uri("imghome2.jpg", mime="image/jpeg")
    landmarks_img = data_uri("landmarks.jpg", mime="image/jpeg")

    # map data (unchanged)
    lat = -15.767818205770041
    lon = -47.86687301603605
    address_html = (
        "Campus Universitário Darcy Ribeiro<br>"
        "Brasília - DF - s/n<br>"
        "CEP 70910-000"
    )
    gmaps_view = f"https://www.google.com/maps?q={lat},{lon}"
    gmaps_dir  = f"https://www.google.com/maps?daddr={lat},{lon}"
    osm_view   = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=17/{lat}/{lon}"
    bbox_w = lon - 0.01; bbox_s = lat - 0.01; bbox_e = lon + 0.01; bbox_n = lat + 0.01
    osm_embed = (
        f"https://www.openstreetmap.org/export/embed.html?"
        f"bbox={bbox_w},{bbox_s},{bbox_e},{bbox_n}&layer=mapnik&marker={lat},{lon}"
    )
    st.markdown(
        f"""
        <style>
      /* --- Hero layout ------------------------------------------------ */
      .hero {{
        display:grid;
        gap: 26px;
        align-items:start;
        grid-template-columns: 1fr;
        grid-template-areas:
          "head"
          "left"
          "center"
          "right";
      }}
      .hero .col-head   {{ grid-area: head; }}
      .hero .col-left   {{ grid-area: left; }}
      .hero .col-center {{ grid-area: center; }}
      .hero .col-right  {{ grid-area: right; }}
      @media (min-width:700px) {{
        .hero {{
          grid-template-columns: 1fr 1fr;
          grid-template-areas:
            "head   head"
            "center center"
            "left   right";
          gap: 28px;
        }}
      }}
      @media (min-width:1100px) {{
        .hero {{
          grid-template-columns: 0.9fr 1.2fr 0.9fr;
          grid-template-areas:
            "head   head   head"
            "left   center right";
          gap: 32px;
        }}
        .col-left  {{ justify-self:start; }}
        .col-right {{ justify-self:end;   }}
        .col-left .imgframe, .col-right .imgframe {{ width:88%; }}
      }}
      .title {{
        font-size: clamp(32px, 5vw, 56px);
        font-weight: 800;
        color: var(--TEXT_DARK, #0f172a);
        margin: 6px 0 12px;
        line-height: 1.08;
        letter-spacing: -0.01em;
      }}
      .col-head {{ text-align:center; display:flex; flex-direction:column; align-items:center; }}
      .col-head .title {{ text-align:center; position:relative; }}
      .col-head .title::after {{
        content:"";
        display:block;
        height:3px;
        width:84px;
        margin:10px auto 0;
        border-radius:3px;
        background:linear-gradient(90deg, var(--primary, #1351d8), rgba(19,81,216,.25));
      }}
      .lead {{ color:#374151; line-height:1.75; font-size:17px; max-width:72ch; }}
      .hero .title + .lead {{
        color: var(--primary, #1351d8);
        font-weight: 700;
        font-size: clamp(18px, 2.1vw, 20px);
        line-height: 1.55;
        margin-top: 14px;
        text-align:center;
      }}
      .wrap a {{
        color: var(--primary, #1351d8);
        text-decoration: none;
        border-bottom: 1px dashed rgba(19,81,216,.35);
      }}
      .wrap a:hover {{ text-decoration: underline; }}
      .imgframe {{
        border:1px solid #e7e7ef;
        border-radius:16px;
        overflow:hidden;
        background:#fff;
        box-shadow: 0 12px 34px rgba(2,6,23,.10);
        transition: transform .25s ease, box-shadow .25s ease;
      }}
      .imgframe img {{ width:100%; height:auto; display:block; }}
      .imgframe:hover {{ transform: translateY(-2px); box-shadow:0 16px 42px rgba(2,6,23,.14); }}
      @media (prefers-reduced-motion: reduce) {{ .imgframe, .stack-card {{ transition:none; transform:none; }} }}
      .col-center .stack-cards {{ max-width:72ch; margin:10px auto 0; display:grid; grid-template-columns:1fr; gap:18px; }}
      .stack-card {{
        position:relative;
        padding:20px 24px;
        border-radius:16px;
        background:
          linear-gradient(#ffffff, #ffffff) padding-box,
          linear-gradient(180deg, rgba(19,81,216,.20), rgba(19,81,216,0)) border-box;
        border:1px solid #e6eaf4;
        box-shadow: 0 12px 28px rgba(2,6,23,.08);
        transition: box-shadow .25s ease, transform .25s ease;
      }}
      .stack-card:hover {{ transform: translateY(-2px); box-shadow:0 16px 38px rgba(2,6,23,.12); }}
      .stack-card h3 {{
        margin:0 0 8px;
        font-weight: 750;
        font-size: clamp(17px, 1.9vw, 20px);
        line-height:1.28;
        letter-spacing:-.005em;
        color: var(--TEXT_DARK, #0f172a);
      }}
      .stack-card h3::after {{
        content:"";
        display:block;
        height:2px;
        width:54px;
        margin-top:8px;
        border-radius:2px;
        background:linear-gradient(90deg, var(--primary, #1351d8), rgba(19,81,216,.20));
      }}
      .stack-card p {{ margin:10px 0 0; font-size:16.5px; line-height:1.75; color: var(--TEXT_DARK, #0f172a); }}
      .stack-card ul {{ margin:10px 0 0; padding-left: 22px; }}
      .stack-card li {{ margin:4px 0; line-height:1.7; color: var(--TEXT_DARK, #0f172a); }}
      .landmarks {{ margin: 42px auto 6px; }}
      .landmarks .lm-title {{
        text-align:center;
        font-weight:800;
        color: var(--TEXT_DARK, #0f172a);
        font-size: clamp(20px, 3vw, 28px);
        margin: 2px 0 14px;
      }}
      .landmarks .imgframe {{ border-radius:18px; }}
      .landmarks .caption {{
        text-align:center;
        color:#475569;
        font-size: 13.5px;
        margin-top:8px;
      }}
      /* === Map section ================================================= */
      .map-section {{ margin: 26px auto 8px; }}
      .map-title {{
        text-align:center; font-weight:800; color:#0b1220;
        font-size: clamp(20px, 3vw, 28px); margin: 6px 0 14px;
      }}
      .map-grid {{
        display:grid; grid-template-columns:1fr; gap:16px; align-items:stretch;
        max-width: 1180px; margin: 0 auto;
      }}
      @media (min-width: 980px){{
        .map-grid {{ grid-template-columns: 1.2fr .8fr; gap:18px; }}
      }}
      .map-card {{
        position:relative; border-radius:18px; overflow:hidden;
        border:1px solid #e6e8ee; background:#fff;
        box-shadow:0 16px 36px rgba(2,6,23,.12);
      }}
      .map-frame {{ position:relative; width:100%; aspect-ratio:16/9; background:#e5eefb; }}
      .map-frame iframe {{ position:absolute; inset:0; width:100%; height:100%; border:0; }}
      .map-frame::after {{
        content:""; position:absolute; left:50%; top:50%; transform:translate(-50%,-50%);
        width:64px; height:64px; border-radius:50%;
        box-shadow:0 0 0 2px rgba(19,81,216,.25), 0 0 0 12px rgba(19,81,216,.06);
        pointer-events:none;
      }}
      .map-badge {{
        position:absolute; left:12px; top:12px;
        background: rgba(255,255,255,.92);
        border:1px solid #e2e8f0; backdrop-filter: blur(6px);
        padding:4px 10px; border-radius:999px; font-weight:800; font-size:.8rem; color:#0b1220;
      }}
      .info-card {{
        border:1px solid #e6e8ee; border-radius:18px; background:#ffffff;
        box-shadow:0 12px 28px rgba(2,6,23,.08); padding:16px 18px;
      }}
      .info-card h3 {{ margin:0 0 8px; font-size:18px; font-weight:800; color:#0b1220; }}
      .addr {{ color:#111827; line-height:1.6; }}

      .btns {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:12px; }}
      .btn {{
        display:inline-block; padding:10px 14px; border-radius:10px; text-decoration:none; font-weight:900;
        background:var(--primary,#1351d8); color:#ffffff !important; line-height:1;
        text-shadow: 0 1px 0 rgba(0,0,0,.25);
        border: none;
      }}
      .btn.alt {{
        background:#ffffff; color:#0b1220 !important; border:1px solid #dbe2f1;
        text-shadow:none;
      }}
      .wrap a.btn, .wrap a.btn.alt {{ border-bottom: none !important; }}
        </style>
        <div class="wrap">
          <div class="hero">
            <div class="col-head">
              <div class="title">CancerLab – Laboratory of Molecular Pathology of Cancer</div>
              <p class="lead">The Laboratory of Molecular Pathology of Cancer (CancerLab) at the University of Brasília is dedicated to advancing cancer research through the development of innovative liquid biopsy tools and the investigation of molecular targets both genetic and epigenetic that drive carcinogenesis. Our ultimate goal is to translate these discoveries into novel diagnostic and prognostic strategies that can improve cancer treatment and patient care</p>
            </div>
            <!-- Left image -->
            <div class="col-left">
              <div class="imgframe">
                <img src="{left_img}" alt="CancerLab – left illustrative image" />
              </div>
            </div>
            <div class="col-center">
              <div class="stack-cards">
                <article class="stack-card">
                  <h3>Our Mission</h3>
                  <p>We are committed to training highly qualified professionals in innovative techniques of gene editing, genomics, and liquid biopsy. Our work is dedicated to advancing prevention and comprehensive care for oncology patients, while also developing cutting edge products and services that strengthen scientific and technological innovation in health.</p>
                </article>
                <article class="stack-card">
                  <h3>Our Research</h3>
                  <p>Our research focuses on:</p>
                  <ul>
                    <li><strong>Liquid biopsy:</strong> studying circulating tumor DNA (ctDNA) for clinical applications.</li>
                    <li><strong>Epigenetics:</strong> investigating the role of methyltransferase enzymes in solid tumors and leukemias.</li>
                    <li><strong>Gene editing:</strong> developing CRISPR/Cas9-based strategies for selective knockout (KO) in cancer.</li>
                  </ul>
                </article>
                <article class="stack-card">
                  <h3>Our Team</h3>
                  <p>The Laboratory of Molecular Pathology of Cancer (CancerLab) is the operational unit of two research groups at the University of Brasília: <a href='http://dgp.cnpq.br/dgp/espelhogrupo/769498'>Patologia Molecular do Câncer</a> (created in 2008) and <a href='http://dgp.cnpq.br/dgp/espelhogrupo/775959'>Desenvolvimento e Aplicações em Biópsia Líquida</a> (created in 2022). Together, these initiatives bring together researchers dedicated to exploring the molecular mechanisms of human carcinogenesis and translating discoveries into clinical applications.</p>
                  <p>Our team integrates expertise across Clinical Pathology, Molecular Biology, Biochemistry, Immunology, and Genetics creating a truly multidisciplinary environment to drive high-impact research in cancer biology.</p>
                </article>
                <article class="stack-card">
                  <h3>Looking Ahead</h3>
                  <p>We aim to expand our collaborations with leading research centers across Brazil and abroad, fostering student and researcher exchanges that will strengthen our scientific network and amplify the global reach of our discoveries.</p>
                </article>
              </div>
            </div>
            <div class="col-right">
              <div class="imgframe">
                <img src="{right_img}" alt="CancerLab – right illustrative image" />
              </div>
            </div>
          </div>
          <section class="landmarks" aria-label="Landmarks timeline">
            <div class="lm-title">Landmarks</div>
            <div class="imgframe">
              <img src="{landmarks_img}" alt="CancerLab timeline of key milestones" />
            </div>
          </section>
          <!-- Map / Location -->
          <section class="map-section" aria-label="Location map">
            <div class="map-title">Where to find us</div>
            <div class="map-grid">
              <div class="map-card">
                <div class="map-frame">
                  <iframe
                    src="{osm_embed}"
                    loading="lazy"
                    referrerpolicy="no-referrer-when-downgrade"
                    title="CancerLab location map"
                  ></iframe>
                </div>
                <div class="map-badge">OpenStreetMap • Marker at {lat:.6f}, {lon:.6f}</div>
              </div>
              <div class="info-card">
                <h3>Laboratory location</h3>
                <div class="addr">{address_html}</div>
                <!-- removed Lat/Lon chips -->
                <div class="btns">
                  <a class="btn" href="{gmaps_view}" target="_blank" rel="noopener">View on Google Maps</a>
                  <a class="btn alt" href="{osm_view}" target="_blank" rel="noopener">OpenStreetMap</a>
                  <a class="btn" href="{gmaps_dir}" target="_blank" rel="noopener">Directions</a>
                </div>
              </div>
            </div>
          </section>
        </div>
        """,
        unsafe_allow_html=True,
    )















def page_research():
    st.markdown(
        f"""
        <style>
        /* container */
        .wrap {{ max-width:1180px; margin:32px auto; padding:0 16px; }}
        /* ======= HERO (intro band) ======= */
        .r-hero {{
          background: radial-gradient(1200px 300px at 50% -50px, rgba(19,81,216,.12), transparent 60%);
          padding: 14px 0 6px;
          text-align:center;
        }}
        .r-title {{
          font-size: clamp(28px, 4.8vw, 48px);
          font-weight: 800;
          color: var(--TEXT_DARK, #0f172a);
          letter-spacing:-.01em;
          margin: 6px 0 10px;
          line-height:1.08;
        }}
        .r-sub {{
          color: var(--primary, #1351d8);
          font-weight: 750;
          font-size: clamp(18px, 2.1vw, 20px);
          line-height:1.55;
          margin: 8px auto 18px;
          max-width: 80ch;
        }}
        .topic-pills {{
          display:grid;
          grid-template-columns: 1fr;
          gap:12px;
          max-width:980px;
          margin:0 auto 18px;
          text-align:left;
        }}
        @media (min-width:720px){{
          .topic-pills{{ grid-template-columns: repeat(3, minmax(0,1fr)); }}
        }}
        .pill {{
          position:relative;
          display:flex; gap:12px; align-items:flex-start;
          padding:14px 16px;
          border-radius:14px;
          background:#fff;
          border:1px solid #e7e7ef;
          box-shadow: 0 8px 22px rgba(2,6,23,.06);
          transition: transform .2s ease, box-shadow .2s ease;
        }}
        .pill:hover{{ transform: translateY(-2px); box-shadow: 0 14px 30px rgba(2,6,23,.10); }}
        .pill-icon{{
          flex:0 0 36px; height:36px; width:36px; border-radius:10px;
          display:grid; place-items:center;
          background: linear-gradient(180deg, rgba(19,81,216,.12), rgba(19,81,216,.0));
          border:1px solid #dfe3f2;
        }}
        .pill h4{{ margin:0 0 4px; font-size:16px; color: var(--TEXT_DARK, #0f172a); }}
        .pill p{{ margin:0; font-size:14.5px; line-height:1.55; color:#1f2937; }}
        /* ======= MAIN LAYOUT: sticky side + content ======= */
        .r-body{{
          display:grid; gap:24px; align-items:start;
          grid-template-columns: 1fr;
          margin-top: 12px;
        }}
        @media (min-width:980px){{
          .r-body{{ grid-template-columns: .85fr 1.15fr; gap:28px; }}
        }}
        /* side (desktop sticky) */
        .r-side{{
          position:sticky; top:88px;
          background:#fff; border:1px solid #e7e7ef; border-radius:14px;
          padding:14px; box-shadow:0 8px 22px rgba(2,6,23,.06);
        }}
        .r-side h5{{ margin:0 0 10px; font-size:14px; letter-spacing:.04em; text-transform:uppercase; color:#334155; }}
        .toc{{ list-style:none; margin:0; padding:0; }}
        .toc li a{{
          display:block; padding:8px 10px; border-radius:10px; text-decoration:none;
          color: var(--TEXT_DARK, #0f172a); border:1px dashed rgba(19,81,216,.25);
          margin:6px 0;
        }}
        .toc li a:hover{{ background:rgba(19,81,216,.06); }}
        /* content cards */
        .r-content{{ display:grid; gap:18px; }}
        .section{{
          background:#fff; border:1px solid #e7e7ef; border-radius:16px;
          padding:18px 20px; box-shadow:0 12px 28px rgba(2,6,23,.08);
          scroll-margin-top: 96px; /* ensure anchors show below sticky topbar */
        }}
        .section h2{{
          margin:0 0 8px; font-size: clamp(18px, 2.6vw, 24px); line-height:1.25;
          color: var(--TEXT_DARK, #0f172a);
        }}
        .section .lede{{ color:#0f172a; font-weight:600; }}
        .section p{{ margin:10px 0 0; font-size:16.2px; line-height:1.75; color:#1f2937; }}
        .chips{{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }}
        .chip{{
          font-size:12.5px; padding:4px 10px; border-radius:999px;
          border:1px solid #cfd6f3; background:#f7f9ff; color:#0f172a; font-weight:700;
        }}
        /* links keep dashed underline style from site */
        .wrap a{{ color: var(--primary, #1351d8); text-decoration:none; border-bottom:1px dashed rgba(19,81,216,.35); }}
        .wrap a:hover{{ text-decoration:underline; }}
        /* ======= MOBILE FIXES =======
           1) Disable sticky on small screens
           2) Turn TOC into a horizontal, scrollable chip bar
           3) Lighter shadows for smoother scrolling
        */
        @media (max-width: 979px){{
          .r-side{{
            position: static; top:auto;
            box-shadow:none; border:1px dashed rgba(19,81,216,.25); background:#f8fafc;
          }}
          .r-side h5{{ display:none; }}
          .toc{{ 
            display:flex; gap:8px; overflow-x:auto; padding:8px 2px 10px;
            -webkit-overflow-scrolling: touch;
          }}
          .toc li{{ flex:0 0 auto; }}
          .toc li a{{
            margin:0; border-style: solid; background:#fff; white-space:nowrap;
          }}
          .section{{ box-shadow:0 6px 16px rgba(2,6,23,.06); }}
        }}
        </style>
        <div class="wrap">
          <!-- ===== HERO ===== -->
          <section class="r-hero" aria-label="Research overview">
            <div class="r-title">Research</div>
            <p class="r-sub">Our Research is focused on 3 main topics:</p>
            <div class="topic-pills">
              <div class="pill">
                <div class="pill-icon">
                  <!-- droplet -->
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M12 3s6 6.4 6 10.2A6 6 0 1 1 6 13.2C6 9.4 12 3 12 3z" stroke="currentColor" stroke-width="1.6"/>
                  </svg>
                </div>
                <div>
                  <h4>Liquid biopsy tools</h4>
                  <p>The development and application of Liquid biopsy tools.</p>
                </div>
              </div>
              <div class="pill">
                <div class="pill-icon">
                  <!-- helix -->
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M7 3c4 0 4 6 10 6M7 21c4 0 4-6 10-6M7 9c4 0 4-6 10-6M7 15c4 0 4 6 10 6" stroke="currentColor" stroke-width="1.6"/>
                  </svg>
                </div>
                <div>
                  <h4>Cancer epigenetics</h4>
                  <p>The study of methyltransferase enzymes in solid tumors and leukemias.</p>
                </div>
              </div>
              <div class="pill">
                <div class="pill-icon">
                  <!-- edit gene -->
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M4 14c4 0 4-4 8-4m0 0c2 0 3 1 4 2m-4-2c-2 0-3-1-4-2M3 20l3-.6 9.4-9.4a2.1 2.1 0 0 0-3-3L3 16.4 3 20z" stroke="currentColor" stroke-width="1.6"/>
                  </svg>
                </div>
                <div>
                  <h4>CRISPR/Cas9 gene editing</h4>
                  <p>Selective knockout (KO) of cancer-related targets.</p>
                </div>
              </div>
            </div>
          </section>
          <!-- ===== BODY ===== -->
          <div class="r-body">
            <aside class="r-side" aria-label="On this page">
              <h5>On this page</h5>
              <ul class="toc">
                <li><a href="#liquid-biopsy">Liquid Biopsy Applications in Cancer</a></li>
                <li><a href="#epigenetics">Cancer Epigenetics</a></li>
                <li><a href="#gene-editing">CRISPR/Cas9 Gene Editing</a></li>
              </ul>
            </aside>
            <main class="r-content">
              <section id="liquid-biopsy" class="section" aria-labelledby="liquid-biopsy-h">
                <h2 id="liquid-biopsy-h">Liquid Biopsy Applications in Cancer</h2>
                <p class="lede">Our research line focuses on the development and clinical application of liquid biopsy as a non-invasive tool for early cancer detection, real-time monitoring of therapeutic response, and improved patient management.</p>
                <p>We investigate circulating tumor DNA (ctDNA) in blood samples, aiming to identify and quantify genetic alterations associated with oncogenesis and tumor progression. This includes the detection of frequent mutations, gene amplifications, and absolute copy numbers of carcinogenic nucleic acid fragments. Using advanced technologies such as next-generation sequencing (NGS) and digital PCR, we design mutation panels tailored to cancer-specific profiles.
                A key aspect of this work is the evaluation of ctDNA as a diagnostic screening method for early cancer detection, as well as a dynamic biomarker to monitor tumor burden in patients undergoing targeted therapies. This approach enables the real-time assessment of treatment effectiveness and supports more personalized therapeutic decisions.
                We are also applying these strategies to colorectal cancer (CRC), the second most common and third deadliest cancer in Brazil. By assessing the prognostic value of ctDNA in CRC patients, we aim to improve recurrence monitoring and clinical management after surgical resection—the current curative standard of care. This project is supported by CNPq/MS and FAPDF, reinforcing our commitment to translating liquid biopsy into practice for better cancer outcomes.</p>
                <p>A key aspect of this work is the evaluation of ctDNA as a diagnostic screening method for early cancer detection, as well as a dynamic biomarker to monitor tumor burden in patients undergoing targeted therapies. This approach enables the real-time assessment of treatment effectiveness and supports more personalized therapeutic decisions.</p>
                <p>We are also applying these strategies to colorectal cancer (CRC), the second most common and third deadliest cancer in Brazil. By assessing the prognostic value of ctDNA in CRC patients, we aim to improve recurrence monitoring and clinical management after surgical resection—the current curative standard of care. This project is supported by CNPq/MS and FAPDF, reinforcing our commitment to translating liquid biopsy into practice for better cancer outcomes.</p>
                <div class="chips" aria-label="Funding and focus tags">
                  <span class="chip">NGS</span><span class="chip">digital PCR</span><span class="chip">ctDNA</span>
                  <span class="chip">CRC</span><span class="chip">Screening</span><span class="chip">Therapy monitoring</span>
                </div>
              </section>
              <section id="epigenetics" class="section" aria-labelledby="epigenetics-h">
                <h2 id="epigenetics-h">Cancer Epigenetics</h2>
                <p>We studie Cancer Epigenetics focused on the role of methyltransferase enzymes in solid tumors and leukemias</p>
              </section>
              <section id="gene-editing" class="section" aria-labelledby="gene-editing-h">
                <h2 id="gene-editing-h">CRISPR/Cas9 Gene Editing</h2>
                <p>The development and application of CRISPR/Cas9-based Gene editing tools for selective knockout (KO) of cancer-related targets.</p>
              </section>
            </main>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def page_publications():
    import html, urllib.parse, requests
    from collections import defaultdict
    from functools import lru_cache
    import streamlit as st  # ensure imported in your file

    # ====== STYLES ======
    st.markdown(
        """
        <style>
          /* Wrapper & headings */
          .pub-wrap { max-width:1180px; margin:28px auto 40px; padding:0 16px; }
          .pub-h1   { font-weight:900; font-size:clamp(24px,3.6vw,36px); margin:6px 0 8px; color:var(--TEXT_DARK,#0f172a); }
          .pub-sub  { color:#475569; font-size:.98rem; margin: 0 0 16px; }

          /* Year index (anchors) */
          .year-index {
            display:flex; flex-wrap:wrap; gap:8px; margin: 14px 0 22px;
          }
          .year-chip {
            display:inline-block; padding:6px 10px; border:1px solid #e6e8ee; border-radius:999px;
            text-decoration:none; font-weight:700; font-size:.92rem; color:#0f172a; background:#fff;
          }
          .year-chip:hover { border-color:#cdd3e0; }

          /* Year section */
          .year-section { margin: 26px 0 18px; scroll-margin-top: 90px; }
          .year-title {
            font-weight:900; font-size:clamp(18px,2.6vw,24px); color:#0f172a; margin:0 0 10px;
            display:flex; align-items:center; gap:10px;
          }
          .year-count {
            font-weight:700; color:#475569; font-size:.88rem; background:#f1f5f9; border:1px solid #e2e8f0;
            padding:2px 8px; border-radius:999px;
          }

          /* List / item */
          .pub-list { list-style:none; padding:0; margin:0; display:grid; gap:10px; }
          .pub-item {
            background:#fff; border:1px solid #e6e8ee; border-radius:14px;
            padding:12px 14px; display:grid; grid-template-columns: 1fr auto; gap:10px; align-items:start;
            position:relative; overflow:hidden;
          }
          .pub-item::before {
            content:""; position:absolute; left:0; top:0; bottom:0; width:3px; background:linear-gradient(#bfdbfe,#93c5fd);
          }
          .pub-item:hover { box-shadow:0 2px 8px rgba(15,23,42,.06); border-color:#dee2ee; }

          .pub-main {}
          .pub-link { text-decoration:none; color:var(--primary,#1351d8); font-weight:800; }
          .pub-link:hover { text-decoration:underline; }
          .pub-meta { color:#475569; font-size:.92rem; margin-top:4px; }

          .pub-aside { display:flex; gap:8px; align-items:center; }
          .doi-badge {
            display:inline-flex; align-items:center; gap:6px;
            font-size:.78rem; padding:3px 9px; border-radius:999px;
            border:1px solid #cbd5e1; color:#334155; background:#f8fafc; text-decoration:none;
          }
          .doi-badge:hover { border-color:#aab7c7; }
          .ext {
            display:inline-block; width:12px; height:12px;
            background: conic-gradient(from 90deg, #64748b, #94a3b8);
            -webkit-mask: url('data:image/svg+xml;utf8,<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path fill="black" d="M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42 9.3-9.29H14V3z"/><path fill="black" d="M5 5h5V3H3v7h2V5zm0 14v-5H3v7h7v-2H5z"/></svg>') center/contain no-repeat;
                    mask: url('data:image/svg+xml;utf8,<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path fill="black" d="M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42 9.3-9.29H14V3z"/><path fill="black" d="M5 5h5V3H3v7h2V5zm0 14v-5H3v7h7v-2H5z"/></svg>') center/contain no-repeat;
          }

          .pub-footnote { color:#64748b; font-size:.9rem; margin:14px 0 8px; }
          .back-top { display:inline-block; margin:10px 0 0; font-size:.88rem; color:#0f172a; text-decoration:none; }
          .back-top:hover { text-decoration:underline; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ====== DATA (keep your list; you can optionally prefill DOI_CACHE) ======
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

    DOI_CACHE = {
        # Optional: prefill known DOIs to skip lookup, using key "Journal|Title"
        # "Frontiers in Molecular Biosciences|Dithiocarbazate ligands and their Ni(II) complexes with potential biological activity: Structural, antitumor and molecular docking study": "10.xxxx/xxxxx",
    }

    def _key(journal: str, title: str) -> str:
        return f"{journal.strip()}|{title.strip()}"

    @lru_cache(maxsize=256)
    def find_doi(title: str, journal: str = "", year: int | None = None) -> str | None:
        k = _key(journal, title)
        if k in DOI_CACHE:
            return DOI_CACHE[k]
        try:
            params = {"query.bibliographic": title, "rows": 1}
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

    # ====== GROUP BY YEAR ======
    by_year: dict[int, list[dict]] = defaultdict(list)
    for p in PUBLICATIONS:
        by_year[int(p["year"])].append(p)
    years = sorted(by_year.keys(), reverse=True)

    # ====== RENDER ======
    st.markdown('<div class="pub-wrap" id="top">', unsafe_allow_html=True)
    st.markdown('<div class="pub-h1">Publications</div>', unsafe_allow_html=True)
    st.markdown('<div class="pub-sub">Click a title to open.</div>', unsafe_allow_html=True)

    # Year index
    chips = []
    for y in years:
        chips.append(f'<a class="year-chip" href="#year-{y}">{y}</a>')
    st.markdown(f'<nav class="year-index">{"".join(chips)}</nav>', unsafe_allow_html=True)

    # Sections per year
    for y in years:
        items = by_year[y]
        st.markdown(f'<section class="year-section" id="year-{y}">', unsafe_allow_html=True)
        st.markdown(f'<div class="year-title">{y} <span class="year-count">{len(items)}</span></div>', unsafe_allow_html=True)
        st.markdown('<ul class="pub-list">', unsafe_allow_html=True)

        for p in items:
            title = p["title"].strip()
            journal = p["journal"].strip()
            authors = p["authors"].strip()

            doi = find_doi(title, journal, y)
            if doi:
                href = f"https://doi.org/{urllib.parse.quote(doi, safe='/')}"
                badge = f'<a class="doi-badge" href="{href}" target="_blank" rel="noopener" title="Open DOI">DOI <span class="ext" aria-hidden="true"></span></a>'
            else:
                q = urllib.parse.quote_plus(title + " " + journal)
                href = f"https://scholar.google.com/scholar?q={q}"
                badge = f'<a class="doi-badge" href="{href}" target="_blank" rel="noopener" title="DOI not found automatically; open Scholar">Search <span class="ext" aria-hidden="true"></span></a>'

            item_html = f"""
              <li class="pub-item">
                <div class="pub-main">
                  <a class="pub-link" href="{href}" target="_blank" rel="noopener">{html.escape(title)}</a>
                  <div class="pub-meta">{html.escape(authors)} · <i>{html.escape(journal)}</i></div>
                </div>
                <div class="pub-aside">{badge}</div>
              </li>
            """
            st.markdown(item_html, unsafe_allow_html=True)

        st.markdown('</ul>', unsafe_allow_html=True)
        st.markdown('<a class="back-top" href="#top">Back to top ↑</a>', unsafe_allow_html=True)
        st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<div class="pub-footnote"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def page_people():


    # Folder where your photos live. Put files like fabio.jpg here.
    BASE_PHOTO_DIR = Path(__file__).parent / "static" / "people"

    PEOPLE = [
        {"name": "Fábio Pittella Silva, PhD", "role": "Principal Investigator - Labhead",
         "photo": "Pittella.jpeg",
         "bio": "Head of the Laboratory of Molecular Pathology of Cancer at the University of Brasília. Ph.D in Molecular Pathology from the Human Genome Center, University of Tokyo (2008); M.Sc. in Medical Sciences from the University of Tokyo (2004); B.Sc. in Pharmacy and Biochemistry (Clinical Analysis) from the Federal University of Juiz de Fora (2001). At the University of Tokyo’s Human Genome Center, identified and described the genes WDRPUH, TIPUH1, and SMYD3—the first methyltransferase implicated in human carcinogenesis. Professor at the University of Brasília (since 2008), supervising master’s, doctoral, and postdoctoral trainees. Associate researcher in liquid biopsy at the Cancer Precision Medicine Center, Japanese Foundation for Cancer Research (JFCR), Tokyo (since 2018). Visiting professor at Memorial Sloan Kettering Cancer Center, New York (2014–2018), working on methyltransferase inhibitors. Expertise in molecular genetics, with focus on epigenetics, protein methyltransferases, liquid biopsy, and molecular targets for cancer diagnosis/therapy. Ad-hoc consultant to DECIT/SCTIE/MS, CNPq, FAPITEC/SE, and FAPDF; co-founder of the innovation company i.rad.Particles",
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
         "bio": "Head of the Laboratory of Molecular Pathology of Cancer at the University of Brasília. Associate Professor IV in the Department of Pharmacy at the University of Brasília. She earned a BSc in Biological Sciences (UnB, 1997) and a PhD in Biochemistry (University of Basel, 2002). Her PhD explored signal-transduction pathways that drive cellular resistance to targeted anticancer drugs such as trastuzumab. She completed postdoctoral training at The Scripps Research Institute (RNA stability) and the Burnham Institute for Medical Research (cell-adhesion proteins and Rho-family GTPases). Her work spans cell biology, biochemistry, molecular biology, oncology, and pharmacology",
         "degrees": ["BSc in Biological Sciences, University of Brasília (1997)",
                     "PhD in Biochemistry, University of Basel (2002)",
                     "Postdoctoral Fellow in RNA Stability, The Scripps Research Institute, La Jolla",
                     "Postdoctoral Fellow in Adhesion Proteins & Rho-family GTPases, Burnham Institute for Medical Research, La Jolla"],
         "email": "andreabm@unb.br", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/6229434599232057", "orcid": "https://orcid.org/0000-0002-9280-2638"},
        {"name": "Ana Cristina Moura Gualberto, PhD", "role": "Postdoctoral Fellow",
         "photo": "anagualberto.jpg", "bio": "BSc and teaching licensure in Biological Sciences from UFJF, followed by an MSc and PhD in Immunology investigating matrix metalloproteinases in breast cancer, including RNAi-based silencing. She completed a postdoc at UFJF on adipose-tissue exosomes in tumor progression and is currently a postdoctoral fellow at the University of Brasília working with CRISPR/Cas9 genome editing in cancer. Her experience includes immune response, breast-cancer animal models, cell culture, molecular biology, confocal microscopy, histology and immunohistochemistry, and functional assays of migration, proliferation, and cell viability.",
         "degrees": ["BSc and Teaching Licensure in Biological Sciences, Federal University of Juiz de Fora (2008–2012)",
                     "MSc in Biological Sciences (Immunology), Federal University of Juiz de Fora — focus on matrix metalloproteinases as markers of breast cancer progression (2013–2015)",
                     "PhD in Biological Sciences (Immunology), Federal University of Juiz de Fora — RNAi silencing of matrix metalloproteinases in breast cancer progression (2015–2019)",
                     "Postdoctoral Fellow, Federal University of Juiz de Fora — adipose tissue exosomes in breast cancer",
                     "Postdoctoral Fellow, University of Brasília, CRISPR/Cas9 genome editing in cancer (current)"], "email": "", "institution": "Federal University of Juiz de Fora",
         "lattes": "http://lattes.cnpq.br/6338541953564765", "orcid": ""},
        {"name": "Luis Janssen Maia, PhD", "role": "Postdoctoral Fellow",
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
         "photo": "flavio.jpg", "bio": "Master’s graduate and current PhD candidate in Medical Sciences at the University of Brasília, focused on the molecular pathology of colorectal cancer. Holds a Biomedicine degree (UniCEUB, 2017) and a specialization in Imaging from Hospital Israelita Albert Einstein (2019). Qualified in clinical analysis, molecular biology, and imaging. Currently works in the Radiology Department (CT unit) at Hospital Sírio-Libanês in Brasília",
         "degrees": ["BSc in Biomedicine, Centro Universitário de Brasília (2017)",
                     "Postgraduate Specialization in Imaging (Imagenologia), Hospital Israelita Albert Einstein (2019)",
                     "MSc in Medical Sciences (Molecular Pathology of Colorectal Cancer), University of Brasília",
                     "PhD Candidate in Medical Sciences (Molecular Pathology of Colorectal Cancer), University of Brasília"], "email": "flavioalencarbarreto92@gmail.com", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/7778492502300819", "orcid": ""},
        {"name": "Brunna Letícia Oliveira Santana, MSc", "role": "PhD Student",
         "photo": "bru.jpg", "bio": "Biologist with an MSc in Medical Sciences focused on cancer epigenetics, now a PhD candidate at the University of Brasília investigating lysine methyltransferase knockouts to identify molecular and therapeutic biomarkers for acute lymphoblastic leukemia",
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
         {"name": "Athos Silva Oliveira", "lattes": "http://lattes.cnpq.br/5665031794527967", "year": "2023", "activity": "Postdoctoral Fellows"},
         {"name": "Vívian D'Afonseca da Silva Ferreira", "lattes": "http://lattes.cnpq.br/6228921073127080", "year": "2015", "activity": "Postdoctoral Fellows"},
         {"name": "Doralina do Amaral Rabello Ramos", "lattes": "http://lattes.cnpq.br/4636606799429977", "year": "2011", "activity": "Postdoctoral Fellows"},
         {"name": "Luís Henrique Toshihiro Sakamoto", "lattes": "http://lattes.cnpq.br/9517030460820076", "year": "2014", "activity": "Ph.D."},
         {"name": "João Nunes de Mattos Neto", "lattes": "http://lattes.cnpq.br/8975088486815463", "year": "2015", "activity": "Ph.D."},
         {"name": "Alan Jhones Barbosa de Assis", "lattes": "http://lattes.cnpq.br/4200078779107622", "year": "2023", "activity": "M.Sc."},
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
    
    order = ["Postdoctoral Fellows","Ph.D.","M.Sc.","PIBIC",""]
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
    Partners & Collaborators
    - Uses the EXACT PARTNERS list provided by you (unchanged)
    - Renders 'Partners' (labs/orgs) and 'Collaborators' (people) in separate sections
    - Logos/photos expected in static/partners/
    """
    import streamlit as st
    from html import escape
    from pathlib import Path
    from textwrap import dedent
    BASE_LOGO_DIR = Path(__file__).parent / "static" / "partners"
    # ========= YOUR ORIGINAL DATA (UNMODIFIED) =========
    PARTNERS = [
        {
            "name": "Cancer Institute of the State of São Paulo (ICESP)",
            "website": "https://icesp.org.br/cto/",
            "logo": "icesp.jpg",
            "country": "São Paulo - Brazil",
            "summary": "ICESP’s CTO is a Latin American center of excellence for translational cancer research, with advanced labs (sequencing, flow cytometry, BSL-2), the USP Biobank, and ~20 groups spanning innovation, molecular oncology, epidemiology/prevention, health economics, and clinical trials"
        },
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
    # ========= STYLES =========
    st.markdown("""
    <style>
      :root {
        --brand:#040359;
        --ink: var(--TEXT_DARK, #0f172a);
        --muted:#4b5563;
        --line:#e5e7eb;
        --card:#ffffff;
      }
      .partners-wrap{ max-width:1180px; margin:0 auto; padding:0 16px 28px; }
      .page-title{ font-size:clamp(24px,3.4vw,34px); font-weight:900; color:var(--ink); margin:18px 0 6px; }
      .index { display:flex; flex-wrap:wrap; gap:8px; margin: 6px 0 18px; }
      .chip  { display:inline-block; padding:6px 10px; border:1px solid #e6e8ee; border-radius:999px;
               text-decoration:none; font-weight:700; font-size:.92rem; color:#0f172a; background:#fff; }
      .chip:hover { border-color:#cfd6e6; }
      .section { margin: 8px 0 24px; scroll-margin-top:90px; }
      .section-title{ font-size:clamp(18px,2.6vw,24px); font-weight:900; color:var(--ink); margin:10px 0 12px; }
      .grid{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:18px; }
      .card{
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
      .card:hover{
        transform:translateY(-2px);
        box-shadow:0 8px 18px rgba(2,6,23,.08);
        border-color:#d9dde3;
      }
      .logo{
        width:64px;height:64px;border-radius:12px;object-fit:contain;
        border:1px solid var(--line); background:#fff;
      }
      .logo-ph{
        width:64px;height:64px;border-radius:12px;border:1px solid var(--line);
        display:flex;align-items:center;justify-content:center;font-weight:800;color:#9ca3af;background:#f8fafc;
      }

      .title a{ color:var(--brand); font-weight:800; text-decoration:none; }
      .title a:hover{ text-decoration:underline; }
      .summary{ color:var(--muted); margin-top:4px; line-height:1.45; font-size:.95rem; }
      .badge{ display:inline-block; font-size:.78rem; padding:2px 10px; border-radius:999px;
              border:1px solid #cbd5e1; margin-top:8px; color:#334155; background:#f8fafc; }
    </style>
    """, unsafe_allow_html=True)
    # ========= helpers =========
    def _logo_html(logo_filename: str, name: str) -> str:
        if logo_filename:
            path = BASE_LOGO_DIR / logo_filename
            if path.exists():
                ext = path.suffix.lower()
                mime = "image/png" if ext==".png" else ("image/webp" if ext==".webp" else "image/jpeg")
                src = data_uri(str(Path("static/partners")/logo_filename), mime=mime)
                return f'<img class="logo" src="{src}" alt="{escape(name)} logo"/>'
        initials = "".join([w[0] for w in name.split()[:2]]).upper() or "?"
        return f'<div class="logo-ph">{initials}</div>'
    def _grid(items: list[dict]) -> str:
        blocks = ['<div class="grid">']
        for p in items:
            name = escape(p.get("name",""))
            website = (p.get("website") or "").strip()
            summary = escape(p.get("summary",""))
            country = escape(p.get("country",""))
            logo = (p.get("logo") or "").strip()
            logo_html = _logo_html(logo, name)
            title_html = f'<a href="{escape(website)}" target="_blank" rel="noopener">{name}</a>' if website else name
            summary_html = f'<div class="summary">{summary}</div>' if summary else ""
            badge_html = f'<div class="badge">{country}</div>' if country else ""
            blocks.append(dedent(f"""
            <div class="card">
              {logo_html}
              <div>
                <div class="title">{title_html}</div>
                {summary_html}
                {badge_html}
              </div>
            </div>
            """).strip())
        blocks.append("</div>")
        return "".join(blocks)
    # ========= classification WITHOUT changing data =========
    def is_collaborator(item: dict) -> bool:
        n = (item.get("name") or "").lower()
        # Individuals in your list carry "phd" (or "md"). Keep logic minimal and non-invasive.
        return ("phd" in n) or (" md" in n) or ("m.d." in n)
    LABS = [p for p in PARTNERS if not is_collaborator(p)]
    PEOPLE = [p for p in PARTNERS if is_collaborator(p)]
    # ========= render =========
    st.markdown('<div class="partners-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Partners & Collaborators</div>', unsafe_allow_html=True)
    st.markdown("""
      <nav class="index">
        <a class="chip" href="#partners">Partners</a>
        <a class="chip" href="#collaborators">Collaborators</a>
      </nav>
    """, unsafe_allow_html=True)
    # Partners (labs)
    st.markdown('<section class="section" id="partners">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Partners</div>', unsafe_allow_html=True)
    st.markdown(_grid(LABS), unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)
    # Collaborators (people)
    st.markdown('<section class="section" id="collaborators">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Collaborators</div>', unsafe_allow_html=True)
    st.markdown(_grid(PEOPLE), unsafe_allow_html=True)
    st.markdown('</section>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def page_positions():
    import html
    from pathlib import Path
    import streamlit as st

    # ---------- helpers ----------
    def _find_video(basename: str = "open") -> Path | None:
        exts = [".mp4", ".webm", ".mov", ".m4v"]
        dirs = [
            Path(__file__).parent / "static" / "videos",
            Path(__file__).parent / "static",
            Path(__file__).parent,
        ]
        for d in dirs:
            for ext in exts:
                p = d / f"{basename}{ext}"
                if p.exists():
                    return p
        return None

    def _mime_for(p: Path | None) -> str:
        if not p:
            return "video/mp4"
        s = p.suffix.lower()
        if s in (".mp4", ".m4v"): return "video/mp4"
        if s == ".webm":           return "video/webm"
        if s == ".mov":            return "video/quicktime"
        return "video/mp4"

    def _video_data_uri(p: Path | None) -> str | None:
        # Prefer using your existing data_uri() helper if available
        try:
            return data_uri(str(p), mime=_mime_for(p)) if p else None
        except Exception:
            return None

    # ---------- content (edit freely) ----------
    HERO_TITLE = "Open Positions"
    HERO_SUB = ""

    TXT_GRAD = (
        "All year around, the CancerLab is open to students interested in obtaining a "
        "Master and PhD degree through the institutional program of Molecular Pathology and Medical Sciences "
        "of the University of Brasilia. Please contact the respective professors via "
        '<a href="mailto:pittella@unb.br">pittella@unb.br</a> or '
        '<a href="mailto:andreabm@unb.br">andreabm@unb.br</a>.'
    )

    TXT_POSTDOC = (
        "Postdoctoral candidates with experience in genetics, biochemistry, molecular biology or bioinformatics "
        "should send a cover letter with expected starting date, Curriculum vitae and names of THREE references to "
        '<a href="mailto:pittella@unb.br">pittella@unb.br</a>.'
    )

    TXT_UNDERGRAD = (
        "The CancerLab is open to undergraduates with major in biology, biotechnology, pharmaceutical sciences, "
        "medicine and health sciences. Students should contact Prof. Fabio Pittella "
        '(<a href="mailto:pittella@unb.br">pittella@unb.br</a>) or Andrea Motoyama '
        '(<a href="mailto:andreabm@unb.br">andreabm@unb.br</a>).'
    )

    REQS = ["Cover letter", "CV", "Names of three references"]

    # ---------- styles ----------
    st.markdown(
        """
        <style>
          .wrap { max-width:1180px; margin:28px auto 44px; padding:0 16px; }
          .h1   { font-weight:900; font-size:clamp(24px,3.6vw,36px); color:#0f172a; margin:6px 0 6px; }
          .lead { color:#475569; margin:0 0 18px; font-size:1.02rem; }

          /* Anchor index */
          .index { display:flex; flex-wrap:wrap; gap:8px; margin: 8px 0 18px; }
          .chip  { display:inline-block; padding:6px 10px; border:1px solid #e6e8ee; border-radius:999px;
                   text-decoration:none; font-weight:700; font-size:.92rem; color:#0f172a; background:#fff; }
          .chip:hover { border-color:#cfd6e6; }

          /* Hero grid */
          .hero { display:grid; gap:18px; grid-template-columns: 1fr; }
          @media (min-width: 980px){ .hero { grid-template-columns: 1.05fr 0.95fr; } }

          .vcard, .tcard {
            background:#fff; border:1px solid #e6e8ee; border-radius:16px; overflow:hidden;
            box-shadow:0 10px 26px rgba(2,6,23,.06);
          }
          .vcard .media { background:#000; aspect-ratio:16/9; }
          .vcard video, .vcard iframe { width:100%; height:100%; display:block; }
          .tcard { padding:16px 18px; }
          .tcard h3 { margin:0 0 8px; font-size:18px; color:#0f172a; }
          .muted { color:#334155; font-size:.94rem; }
          .btns { display:flex; gap:10px; margin-top:12px; flex-wrap:wrap; }
          .btn  { display:inline-block; padding:8px 12px; border-radius:10px; text-decoration:none; font-weight:800;
                  background:var(--primary,#1351d8); color:#fff; }

          /* Sections */
          .section { margin:26px 0 0; scroll-margin-top:90px; }
          .stitle   { display:flex; align-items:center; gap:10px;
                      font-weight:900; font-size:clamp(18px,2.6vw,24px); color:#0f172a; margin:0 0 8px; }
          .scard    { background:#fff; border:1px solid #e6e8ee; border-radius:14px; padding:14px 16px; }
          .scard p  { margin:8px 0; color:#1f2937; line-height:1.65; }
          .ul { margin:8px 0 0 18px; }
          .ul li { margin:4px 0; }

          /* Small accent on section cards */
          .scard { position:relative; }
          .scard::before { content:""; position:absolute; left:0; top:0; bottom:0; width:3px;
                           background:linear-gradient(#bfdbfe,#93c5fd); border-top-left-radius:14px; border-bottom-left-radius:14px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---------- locate video & decide render path ----------
    video_path = _find_video("open")
    video_data = _video_data_uri(video_path)  # prefer embedding to keep layout tight

    # ---------- render ----------
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    st.markdown(f'<div class="h1">{HERO_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="lead">{html.escape(HERO_SUB)}</p>', unsafe_allow_html=True)

    # Anchor index
    st.markdown(
        """
        <nav class="index">
          <a class="chip" href="#grad">Graduate Students</a>
          <a class="chip" href="#postdoc">Postdoctoral Fellows</a>
          <a class="chip" href="#undergrad">Undergraduate Students</a>
          <a class="chip" href="#requirements">Application Requirements</a>
        </nav>
        """,
        unsafe_allow_html=True,
    )

    # Hero grid: video + quick apply
    st.markdown('<section class="hero">', unsafe_allow_html=True)

    # Video card
    if video_data:
        st.markdown(
            f"""
            <div class="vcard">
              <div class="media">
                <video controls preload="metadata" src="{video_data}"></video>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif video_path:
        # Fallback: use Streamlit's video player (cannot be wrapped by our HTML box)
        left, right = st.columns((1.05, 0.95), gap="large")
        with left:
            st.video(str(video_path))
        with right:
            st.markdown(
                f"""
                <div class="tcard">
                  <h3>How to apply</h3>
                  <p class="muted">Send your materials to the appropriate contact below.</p>
                  <div class="btns">
                    <a class="btn" href="mailto:pittella@unb.br?subject=Application%20-%20CancerLab">Email Prof. Pittella</a>
                    <a class="btn" href="mailto:andreabm@unb.br?subject=Application%20-%20CancerLab">Email Prof. Motoyama</a>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</section>', unsafe_allow_html=True)
    else:
        # No video found anywhere — show pretty placeholder + guidance
        st.markdown(
            """
            <div class="vcard">
              <div class="media" style="display:flex;align-items:center;justify-content:center;color:#e2e8f0;">
                <div style="text-align:center;padding:24px;">
                  <div style="font-weight:800;color:#f8fafc;margin-bottom:8px;">Presentation video not found</div>
                  <div style="color:#cbd5e1;font-size:.95rem;">
                    Put <code>open.mp4</code> (or .webm, .mov) in <code>static/videos/</code>, <code>static/</code> or the app folder.
                  </div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="tcard">
              <h3>How to apply</h3>
              <p class="muted">Send your materials to the appropriate contact below.</p>
              <div class="btns">
                <a class="btn" href="mailto:pittella@unb.br?subject=Application%20-%20CancerLab">Email Prof. Pittella</a>
                <a class="btn" href="mailto:andreabm@unb.br?subject=Application%20-%20CancerLab">Email Prof. Motoyama</a>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</section>', unsafe_allow_html=True)

    # If we successfully embedded the video as data URI, add the right-side card now (keeps our HTML grid intact)
    if video_data:
        st.markdown(
            """
            <div class="tcard">
              <h3>How to apply</h3>
              <p class="muted">Send your materials to the appropriate contact below.</p>
              <div class="btns">
                <a class="btn" href="mailto:pittella@unb.br?subject=Application%20-%20CancerLab">Email Prof. Pittella</a>
                <a class="btn" href="mailto:andreabm@unb.br?subject=Application%20-%20CancerLab">Email Prof. Motoyama</a>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</section>', unsafe_allow_html=True)

    # Sections
    st.markdown(
        f"""
        <section class="section" id="grad">
          <div class="stitle">Graduate Students</div>
          <div class="scard"><p>{TXT_GRAD}</p></div>
        </section>

        <section class="section" id="postdoc">
          <div class="stitle">Postdoctoral Fellows</div>
          <div class="scard">
            <p>{TXT_POSTDOC}</p>
            <ul class="ul">
              <li>Expected start date in the cover letter</li>
              <li>Curriculum vitae</li>
              <li>Names of <strong>three</strong> references</li>
            </ul>
          </div>
        </section>

        <section class="section" id="undergrad">
          <div class="stitle">Undergraduate Students</div>
          <div class="scard"><p>{TXT_UNDERGRAD}</p></div>
        </section>

        <section class="section" id="requirements">
          <div class="stitle">Application Requirements</div>
          <div class="scard">
            <ul class="ul">
              {''.join(f'<li>{html.escape(req)}</li>' for req in REQS)}
            </ul>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


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

st.markdown("""
<style>
/* Remove Streamlit's built-in top chrome */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }
/* Pull content up after removing the header */
main .block-container { padding-top: 0 !important; }
html, body { margin-top: 0 !important; }
</style>
""", unsafe_allow_html=True)


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
    elif active_nav in {"home", "research", "publications", "people", "partners", "positions", "equipment"}:  # + two slugs
        {
         "home": page_home,
         "research": page_research,
         "publications": page_publications,
         "people": page_people,
         "partners": page_partners,
         "positions": page_positions,      # + map       # + map
        }[active_nav]()
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

    








