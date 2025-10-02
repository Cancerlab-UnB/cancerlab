# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 18:58:02 2025

@author: victor fleck morais
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
    page_icon=Image.open(ICON_PATH), 
    layout="wide"
)

def data_uri(relpath: str, mime="image/jpeg") -> str:
    p = Path(__file__).parent / relpath
    with open(p, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"

# ====================== Public Page inicio ======================
PRIMARY_BLUE = "#4160BA"   # ajuste de cor 
TEXT_DARK = "#1b1f24"

# slug -> menu central 
PAGES_PUBLIC = [
    ("home", "home"),
    ("research", "research"),
    ("publications", "publications"),
    ("equipment", "equipment"),
    ("people", "people"),  
    ("partners", "partners"),
    ("positions", "open positions"),   # + add this
    ("login", "Internal Access"),
]
def show_help_widget(
    name: str = "Victor Fleck",
    email: str = "Victor.fleck906438@gmail.com",
    role: str = "Undergraduate Pharmacy Student • Web Developer",
    phone: str | None = "+55 61 991281207",
    label: str = "Help",
    accent_css_var: str = "var(--bar-bg, #3f5eb5)",  # inherits your navbar blue
):
    import streamlit as st
    import html as _html
    import urllib.parse as _uq

    # prefilled email
    subject = _uq.quote("Website issue – support request")
    body = _uq.quote(
        "Hi,\n\nI found a problem on the site.\n"
        "- What I was doing:\n- What happened:\n- Expected behavior:\n\nThanks!"
    )
    mailto = f"mailto:{_uq.quote(email.strip())}?subject={subject}&body={body}"

    # optional phone links
    tel_link = f"tel:{_uq.quote(phone)}" if phone else ""
    wa_link  = f"https://wa.me/{''.join([c for c in (phone or '') if c.isdigit()])}" if phone else ""

    st.markdown(
        f"""
        <style>
          :root {{
            --help-accent: {accent_css_var};
            --help-ink: #0f172a;
            --help-muted: #5a6881;
            --help-line: #e9edf6;
            --help-glass: rgba(255,255,255,.65);
            --help-glass-brd: rgba(255,255,255,.55);
          }}

          .help-root {{
            position: fixed; right: 14px; bottom: 14px; z-index: 1100;
            font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
          }}
          .help-toggle {{ display:none; }}

          /* --- MINI FLOATING BUTTON --- */
          .help-fab {{
            position: fixed; right: 14px; bottom: 14px;
            width: 46px; height: 46px; border-radius: 999px;
            display:inline-flex; align-items:center; justify-content:center; gap:10px;
            background:
              radial-gradient(120% 120% at 50% 0%, rgba(255,255,255,.16), rgba(255,255,255,0)),
              var(--help-accent);
            color:#fff; border:1px solid rgba(255,255,255,.45);
            box-shadow: 0 12px 26px rgba(2,6,23,.18);
            cursor:pointer; user-select:none; text-decoration:none;
            transition: transform .15s ease, box-shadow .15s ease, background .2s ease;
            backdrop-filter: saturate(140%) blur(2px);
            -webkit-backdrop-filter: saturate(140%) blur(2px);
          }}
          .help-fab:hover {{ transform: translateY(-1px); box-shadow: 0 16px 34px rgba(2,6,23,.22); }}
          .help-fab svg {{ width:20px; height:20px; }}

          /* --- GLASS POPOVER (COMPACT) --- */
          .help-backdrop {{
            position: fixed; inset: 0; background: rgba(2,6,23,.08);
            opacity:0; pointer-events:none; transition: opacity .15s ease;
          }}
          .help-card {{
            position: fixed; right: 14px; bottom: 66px; width: min(92vw, 320px);
            background: var(--help-glass);
            color: var(--help-ink);
            border-radius: 16px;
            border:1px solid var(--help-glass-brd);
            box-shadow: 0 22px 44px rgba(2,6,23,.22);
            transform: translateY(8px) scale(.99);
            opacity:0; pointer-events:none;
            transition: transform .18s ease, opacity .18s ease, box-shadow .18s ease;
            backdrop-filter: blur(12px) saturate(120%);
            -webkit-backdrop-filter: blur(12px) saturate(120%);
            overflow:hidden;
          }}
          .help-header {{
            display:flex; align-items:center; justify-content:space-between; gap:10px;
            padding: 10px 12px;
            background:
              linear-gradient(180deg, rgba(255,255,255,.45), rgba(255,255,255,.15)),
              var(--help-accent);
            color:#fff; border-bottom:1px solid rgba(255,255,255,.45);
          }}
          .help-title {{ margin:0; font-weight:900; font-size:.98rem; letter-spacing:.2px; }}
          .help-close {{
            width:28px; height:28px; border-radius:10px; border:1px solid rgba(255,255,255,.6);
            background: rgba(255,255,255,.15); color:#fff;
            display:inline-flex; align-items:center; justify-content:center; cursor:pointer; text-decoration:none;
          }}
          .help-body {{ padding: 12px; }}
          .help-meta {{ font-size:.92rem; color:var(--help-muted); margin:6px 0 10px; }}
          .help-strong {{ font-weight:900; color:var(--help-ink); }}

          .row {{ display:flex; flex-wrap:wrap; gap:8px; }}
          .btn, .btn-ghost {{
            display:inline-flex; align-items:center; gap:8px; text-decoration:none; font-weight:800;
            padding:10px 12px; border-radius:12px; font-size:.9rem;
            transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease, background .12s ease;
          }}
          .btn {{ background: var(--help-accent); color:#fff; border:1px solid rgba(255,255,255,.55);
                 box-shadow: 0 10px 24px rgba(2,6,23,.18); }}
          .btn:hover {{ transform: translateY(-1px); box-shadow: 0 14px 28px rgba(2,6,23,.22); }}
          .btn-ghost {{ background: rgba(255,255,255,.75); color: var(--help-ink); border:1px solid var(--help-line); }}
          .btn-ghost:hover {{ transform: translateY(-1px); border-color:#cbd5e1; box-shadow:0 8px 18px rgba(2,6,23,.10); }}
          /* Toggle ON */
          #help-pop:checked ~ .help-backdrop {{ opacity:1; pointer-events:auto; }}
          #help-pop:checked ~ .help-card {{ opacity:1; transform: translateY(0) scale(1); pointer-events:auto; }}
          /* Accessibility */
          .help-card a:focus {{ outline:none; box-shadow:0 0 0 3px rgba(59,130,246,.35); border-radius:12px; }}
          @media (prefers-reduced-motion: reduce) {{ .help-fab, .help-card {{ transition: none; }} }}
        </style>
        <div class="help-root" aria-live="polite">
          <input id="help-pop" class="help-toggle" type="checkbox" />
          <!-- Floating mini button -->
          <label class="help-fab" for="help-pop" title="Get help">
            <!-- Lifebuoy icon -->
            <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="9"></circle>
              <circle cx="12" cy="12" r="3.5"></circle>
              <path d="M4.9 4.9l3.2 3.2M19.1 4.9l-3.2 3.2M4.9 19.1l3.2-3.2M19.1 19.1l-3.2-3.2"></path>
            </svg>
          </label>
          <!-- Backdrop for closing -->
          <label class="help-backdrop" for="help-pop" aria-hidden="true"></label>
          <!-- Glass popover -->
          <aside class="help-card" role="dialog" aria-modal="true" aria-labelledby="help-title">
            <div class="help-header">
              <h4 id="help-title" class="help-title">Problems with the Website?</h4>
              <label for="help-pop" class="help-close" title="Close">✕</label>
            </div>
            <div class="help-body">
              <div class="help-meta">
                <span class="help-strong">{_html.escape(name)}</span> — {_html.escape(role)}
              </div>
              <div class="row" style="margin-bottom:10px;">
                <a class="btn" href="{mailto}" target="_blank" rel="noopener" aria-label="Email">
                  <!-- mail icon -->
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <rect x="3" y="5" width="18" height="14" rx="2" ry="2"></rect>
                    <path d="M3 7l9 6 9-6"></path>
                  </svg>
                  Email
                </a>
                {"<a class='btn-ghost' href='"+_html.escape(tel_link)+"' aria-label='Call'><svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%230f172a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'><path d='M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 1.09 4.18 2 2 0 0 1 3.1 2h3a2 2 0 0 1 2 1.72c.12.9.34 1.78.66 2.61a2 2 0 0 1-.45 2.11L7.09 9.91a16 16 0 0 0 6 6l1.47-1.22a2 2 0 0 1 2.11-.45c.83.32 1.71.54 2.61.66A2 2 0 0 1 22 16.92z'/></svg>Call</a>" if phone else ""}
                {"<a class='btn-ghost' href='"+_html.escape(wa_link)+"' target='_blank' rel='noopener' aria-label='WhatsApp'><svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%230f172a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'><path d='M20.52 3.48A11.5 11.5 0 0 0 2.6 18.39L2 22l3.72-.58A11.5 11.5 0 1 0 20.52 3.48Z'/><path d='M7 10.5s1 3 5 5 3-2 3-2'/></svg>WhatsApp</a>" if phone else ""}
              </div>
              <a class="btn-ghost" href="{mailto}" target="_blank" rel="noopener">Report a problem</a>
            </div>
          </aside>
        </div>
        """,
        unsafe_allow_html=True,
    )




def show_lab_header(
    image_relpath: str = "static/imgfront",
    address_lines: tuple[str, ...] = (
        "Laboratory of Molecular Pathology of Cancer",
        "Faculty of Health Sciences",
        "University of Brasília",
        "Brasília – DF – Brazil",
    ),
    logo_height_px: int = 110,   # tweak to taste
):
    import base64, mimetypes
    from pathlib import Path
    import streamlit as st

    # resolve image path even if extension not provided
    p = Path(image_relpath)
    if not p.suffix:
        for ext in (".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif"):
            cand = p.with_suffix(ext)
            if cand.exists():
                p = cand
                break

    img_tag = ""
    if p.exists():
        mime = mimetypes.guess_type(str(p))[0] or "image/png"
        b64 = base64.b64encode(p.read_bytes()).decode()
        img_tag = (
            f'<a href="?page=home" class="logo-link" aria-label="Home">'
            f'  <img class="logo" src="data:{mime};base64,{b64}" alt="Lab logo" loading="eager" decoding="async">'
            f'</a>'
        )

    mobile_logo_h = max(60, logo_height_px - 32)

    st.markdown(
        f"""
        <style>
          /* Card-like header to match the site vibe */
          .brand-header {{
            background:
              linear-gradient(180deg, rgba(63,94,181,.06), rgba(63,94,181,0)),
              #fff;
            border: 1px solid rgba(2,6,23,.06);
            border-radius: 14px;
            box-shadow: 0 10px 24px rgba(2,6,23,.06);
            margin: 0 auto 10px;
          }}
          .brand-wrap {{
            max-width:1180px;
            margin:0 auto;
            padding: 18px 18px;
            display:grid;
            grid-template-columns:auto 1fr; /* logo | address */
            align-items:center;
            gap:28px;
          }}
          /* Bigger, crisp logo */
          .brand-header .logo {{
            height:{logo_height_px}px;
            max-height:26vh;
            width:auto; display:block;
            filter: drop-shadow(0 1px 0 rgba(0,0,0,.04));
          }}
          .brand-header .logo-link {{ text-decoration:none; line-height:0; }}
          /* Modern address block */
          .brand-header .addr {{
            text-align:right;
            color: var(--TEXT_DARK, #0f172a);
            letter-spacing:.15px;
          }}
          .brand-header .addr .lab {{
            display:block;
            font-weight:800;
            font-size:clamp(20px, 2.0vw, 24px);
            line-height:1.12;
          }}
          /* subtle accent underline */
          .brand-header .addr .lab::after {{
            content:"";
            display:block;
            width:64px; height:3px; border-radius:2px;
            background: rgba(63,94,181,.45);  /* soft blue accent */
            margin:10px 0 8px auto;           /* right aligned */
          }}
          .brand-header .addr .muted {{
            opacity:.9;
            font-weight:700;
            font-size:clamp(13.5px, 1.05vw, 15.5px);
            line-height:1.28;
          }}
          /* Mobile: stack nicely */
          @media (max-width:900px){{
            .brand-wrap {{ grid-template-columns:1fr; gap:12px; padding:16px 14px; }}
            .brand-header .addr {{ text-align:center; }}
            .brand-header .logo {{ height:{mobile_logo_h}px; margin:0 auto; }}
            .brand-header .addr .lab::after {{ margin-left:auto; margin-right:auto; }}
          }}
        </style>
        <div class="brand-header" role="banner" aria-label="Laboratory heading">
          <div class="brand-wrap">
            <div class="brand-left">{img_tag}</div>
            <div class="addr">
              <span class="lab">{address_lines[0]}</span>
              <span class="muted">{'<br>'.join(address_lines[1:])}</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )




def _get_param(key: str, default=None):
    try:
        params = st.query_params     # Streamlit >= 1.32
        val = params.get(key, default)
        if isinstance(val, (list, tuple)):
            return val[0]
        return val
    except Exception:
        params = st.experimental_get_query_params()  
        return params.get(key, [default])[0] if params.get(key) else default

def _set_param(**kwargs):
    try:
        st.query_params.update(kwargs)
    except Exception:
        st.experimental_set_query_params(**kwargs)
        
def show_front_strip(
    caption: str = "Welcome to the lab — advancing genomics & ctDNA",
    image_relpath: str = "static/imgfront"   # we’ll auto-detect the extension
):
    import base64, mimetypes
    from pathlib import Path
    import streamlit as st

    # --- resolve the image path even if no extension was provided ---
    p = Path(image_relpath)
    if not p.suffix:
        for ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"):
            cand = p.with_suffix(ext)
            if cand.exists():
                p = cand
                break
    if not p.exists():
        # fail gracefully: show only the caption bar
        img_tag = ""
    else:
        mime = mimetypes.guess_type(str(p))[0] or "image/png"
        b64 = base64.b64encode(p.read_bytes()).decode()
        img_uri = f"data:{mime};base64,{b64}"
        img_tag = f'<img class="front-img" src="{img_uri}" alt="front image">'

    st.markdown(
        f"""
        <style>
          .front-strip {{
            position: fixed; top: 0; left: 0; right: 0;
            z-index: 10000;
            background: var(--front-bg, #f3f9fd); /* soft blue */
            border-bottom: 1px solid rgba(15,23,42,.06);
          }}
          .front-wrap {{
            max-width: 1180px;
            margin: 0 auto;
            padding: 10px 16px;
            display: grid;
            grid-template-columns: 1fr auto;  /* caption | image */
            align-items: center;
            gap: 12px;
            font: 600 14px/1.25 ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
            color: var(--front-ink, #0f172a);
          }}
          .front-caption {{ letter-spacing: .2px; }}
          .front-img {{ display:block; height:34px; width:auto; }}
          /* push the app down so the fixed strip doesn't cover your nav */
          .stApp {{ padding-top: 56px; }}
          @media (max-width:700px) {{
            .front-wrap {{ grid-template-columns: 1fr auto; }}
            .front-img {{ height: 28px; }}
            .stApp {{ padding-top: 52px; }}
          }}
        </style>
        <div class="front-strip">
          <div class="front-wrap">
            <div class="front-caption">{caption}</div>
            {img_tag}
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )


                       
def render_navbar(active: str = "home", unbimg: str | None = None):
    import streamlit as st
    from pathlib import Path

    # ---------- Build the menu HTML first ----------
    items = []
    for slug, label in PAGES_PUBLIC:
        is_active = (active == slug)
        cls = "active" if is_active else ""
        aria = ' aria-current="page"' if is_active else ""
        items.append(f'<a target="_self" class="{cls}" href="?page={slug}"{aria}>{label}</a>')
    menu_html = "".join(items)

    # ---------- Right icons (UnB image + Instagram svg) ----------
    # If unbimg wasn't provided, try some common defaults so it "just works".
    if unbimg is None:
        try:
            # prefer svg > png > jpg
            candidates = [("static/unb.svg", "image/svg+xml"),
                          ("static/unb.png", "image/png"),
                          ("static/unb.jpg", "image/jpeg")]
            for pth, mime in candidates:
                if Path(pth).exists():
                    unbimg = data_uri(pth, mime=mime)
                    break
        except Exception:
            unbimg = ""

    unb_html = (
        f'<a class="icon-img" href="https://www.unb.br/" target="_self" '
        f'rel="noopener" title="Universidade de Brasília">'
        f'  <img src="{unbimg or ""}" alt="UnB" />'
        f'</a>'
    )

    # simple Instagram glyph (white, no color changes)
    instagram_svg = (
        '<svg class="glyph" viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="currentColor" d="M7 2h10a5 5 0 015 5v10a5 5 0 01-5 5H7a5 5 0 01-5-5V7a5 5 0 015-5zm0 2a3 3 0 00-3 3v10a3 3 0 003 3h10a3 3 0 003-3V7a3 3 0 00-3-3H7zm5 3a5 5 0 110 10 5 5 0 010-10zm0 2a3 3 0 100 6 3 3 0 000-6zm6.5-2a1.5 1.5 0 100 3 1.5 1.5 0 000-3z"/>'
        '</svg>'
    )
    ig_html = (
        f'<a class="icon-btn ig" href="https://www.instagram.com/cancerlab_unb/" '
        f'target="_blank" rel="noopener" title="@cancerlab_unb">'
        f'{instagram_svg}<span class="label">Instagram</span></a>'
    )
    icons_html = unb_html + ig_html

    # ---------- Render the bar ----------
    st.markdown(
        f"""
        <style>
          :root {{
            --bar-bg: {PRIMARY_BLUE};
            --bar-shadow: 0 6px 18px rgba(2,6,23,.08);
          }}
          /* Sit tight to the top */
          header[data-testid="stHeader"] {{ height: 0 !important; }}
          .main .block-container {{ padding-top: 0 !important; }}
          div[data-testid="stDecoration"] {{ display:none; }}

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
            display:grid; grid-template-columns: 1fr auto; align-items:center; gap:16px;
          }}

          /* ===== Menu (centered) ===== */
          .menu {{
            display:flex; gap:18px; align-items:center; justify-content:center;
            min-width:0; overflow:auto hidden;
          }}
          .menu::-webkit-scrollbar {{ display:none; }}
          .menu a {{
            position: relative;
            text-decoration:none; color:white; text-transform: lowercase;
            padding:8px 12px; border-radius:10px; font-weight:700; letter-spacing:.2px;
            transition: background .2s ease, color .2s ease, transform .15s ease;
            white-space:nowrap;
          }}
          .menu a:hover {{ background: rgba(255,255,255,.14); transform: translateY(-1px); }}
          .menu a:focus-visible {{ outline:2px solid rgba(255,255,255,.95); outline-offset:2px; }}

          /* Active state */
          .menu a.active, .menu a[aria-current="page"] {{
            background: rgba(255,255,255,.22);
          }}
          .menu a.active::after, .menu a[aria-current="page"]::after {{
            content:""; position:absolute; left:12px; right:12px; bottom:6px; height:2px;
            background: rgba(255,255,255,.9); border-radius:2px;
          }}

          /* ===== Right-side icons ===== */
          .icons {{ display:flex; gap:10px; align-items:center; justify-content:flex-end; }}
          .icon-btn, .icon-img {{
            display:inline-flex; align-items:center; justify-content:center;
            background: rgba(255,255,255,.08);
            border:1px solid rgba(255,255,255,.55);
            color:white; border-radius:10px; padding:7px 12px;
            text-decoration:none; line-height:1; white-space:nowrap;
            transition: background .2s ease, transform .15s ease, border-color .2s ease;
            will-change: transform;
          }}
          .icon-btn:hover, .icon-img:hover {{ background: rgba(255,255,255,.16); transform: translateY(-1px); }}
          .icon-btn:focus-visible, .icon-img:focus-visible {{ outline:2px solid rgba(255,255,255,.95); outline-offset:2px; }}

          /* UnB image button */
          .icon-img img {{
            height:18px; width:auto; display:block; filter: drop-shadow(0 1px 0 rgba(0,0,0,.05));
          }}

          /* Instagram button */
          .icon-btn.ig {{ gap:8px; font-weight:800; }}
          .icon-btn .glyph {{ width:18px; height:18px; flex:0 0 18px; color:#fff; }}
          .icon-btn .label {{ display:inline-block; }}
          @media (max-width:760px) {{
            .topbar-inner {{ grid-template-columns: 1fr; gap:10px; }}
            .icons {{ justify-content:flex-start; }}
            .icon-btn .label {{ display:none; }} /* keep it compact on small screens */
          }}
          @media (prefers-reduced-motion: reduce) {{
            .menu a, .icon-btn, .icon-img {{ transition: none; }}
          }}
        </style>

        <div class="topbar" role="navigation" aria-label="Primary">
          <div class="topbar-inner">
            <nav class="menu">{menu_html}</nav>
            <div class="icons">
              {icons_html}
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )





def show_anniversary_cta(
    image_relpath: str = "static/anniversary13.jpg",
    label: str = "🎉 13 years of scientific innovation",
):
    """Centered CTA -> CSS-only modal with lots of balloons + fireworks (no header)."""
    import base64, mimetypes
    from pathlib import Path
    import uuid
    import streamlit as st

    p = Path(image_relpath)
    if not p.exists():
        return

    mime = mimetypes.guess_type(str(p))[0] or "image/jpeg"
    src  = base64.b64encode(p.read_bytes()).decode()
    data = f"data:{mime};base64,{src}"
    uid = f"anni{uuid.uuid4().hex[:7]}"

    st.markdown(
        f"""
<style>
  :root {{
    --anni-accent: var(--bar-bg, #3f5eb5);
    --anni-ink: #0f172a;
    --anni-line: #e8edf6;
  }}

  .{uid}-row {{
    display:flex; justify-content:center; margin:12px 0 18px;
    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
  }}

  .{uid}-pill {{
    display:inline-flex; align-items:center; gap:10px;
    padding:10px 16px; border-radius:999px; cursor:pointer; user-select:none;
    background:
      radial-gradient(120% 180% at 20% 0%, rgba(255,255,255,.28), rgba(255,255,255,0)),
      var(--anni-accent);
    color:#fff; font-weight:900; letter-spacing:.2px;
    border:1px solid rgba(255,255,255,.55);
    box-shadow:0 10px 24px rgba(2,6,23,.14);
    text-decoration:none; transition:transform .12s ease, box-shadow .12s ease;
  }}
    .{uid}-pill{
      /* ...existing styles... */
      color:#fff !important;           /* <- make the text white */
    }
    .{uid}-pill:link,
    .{uid}-pill:visited,
    .{uid}-pill * { color:#fff !important; }  /* ensure any child spans/strongs also render white */
  #{uid}-toggle {{ display:none; }}

  .{uid}-modal {{
    position: fixed; inset: 0; z-index: 4000;
    display: none; place-items:center;
  }}
  #{uid}-toggle:checked ~ .{uid}-modal {{ display:grid; }}

  .{uid}-backdrop {{
    position:absolute; inset:0; background:rgba(2,6,23,.45);
    backdrop-filter: blur(2px); -webkit-backdrop-filter: blur(2px);
  }}

  .{uid}-fx {{ position:absolute; inset:0; pointer-events:none; overflow:hidden; }}

  /* Balloons (more of them) */
  .{uid}-balloon {{
    position:absolute; bottom:-20vh; width:56px; height:70px; border-radius:50% 50% 46% 46%;
    background: radial-gradient(circle at 35% 28%, rgba(255,255,255,.55), rgba(255,255,255,0) 46%), var(--bclr,#60a5fa);
    filter: drop-shadow(0 6px 10px rgba(2,6,23,.18));
    animation: {uid}-float var(--spd, 11s) ease-in infinite;
    opacity:.95;
  }}
  .{uid}-balloon::after {{
    content:""; position:absolute; left:50%; bottom:-24px; width:2px; height:30px;
    background:rgba(255,255,255,.9); transform:translateX(-50%);
  }}
  @keyframes {uid}-float {{
    0% {{ transform: translateY(0) translateX(0); }}
    50%{{ transform: translateY(-52vh) translateX(12px); }}
    100%{{ transform: translateY(-104vh) translateX(-8px); }}
  }}

  /* Fireworks (more bursts) */
  .{uid}-fw {{
    position:absolute; width:2px; height:2px; border-radius:50%;
    background:transparent; opacity:.9;
    box-shadow:
      0 -14px 0 2px var(--clr,#f59e0b),
      11px -7px 0 2px var(--clr,#f59e0b),
      11px  7px 0 2px var(--clr,#f59e0b),
      0  14px 0 2px var(--clr,#f59e0b),
      -11px 7px 0 2px var(--clr,#f59e0b),
      -11px -7px 0 2px var(--clr,#f59e0b);
    animation: {uid}-boom var(--dur,1.8s) ease-out infinite;
  }}
  .{uid}-fw.small {{
    box-shadow:
      0 -10px 0 2px var(--clr,#22c55e),
      8px -5px 0 2px var(--clr,#22c55e),
      8px  5px 0 2px var(--clr,#22c55e),
      0  10px 0 2px var(--clr,#22c55e),
      -8px 5px 0 2px var(--clr,#22c55e),
      -8px -5px 0 2px var(--clr,#22c55e);
  }}
  @keyframes {uid}-boom {{
    0%   {{ transform: translate(var(--x,50vw), var(--y,50vh)) scale(.2); opacity:0; }}
    10%  {{ opacity:1; }}
    100% {{ transform: translate(var(--x,50vw), var(--y,50vh)) scale(1.5); opacity:0; }}
  }}

  /* Card (no header bar) */
  .{uid}-card {{
    position:relative; max-width:min(92vw, 720px);
    background:rgba(255,255,255,.78);
    border:1px solid rgba(255,255,255,.65);
    border-radius:18px; overflow:hidden;
    box-shadow:0 24px 54px rgba(2,6,23,.28);
    backdrop-filter:blur(12px) saturate(120%); -webkit-backdrop-filter:blur(12px) saturate(120%);
    transform:translateY(8px) scale(.99); transition:transform .18s ease;
  }}
  #{uid}-toggle:checked ~ .{uid}-modal .{uid}-card {{ transform:translateY(0) scale(1); }}

  /* Corner close button */
  .{uid}-close {{
    position:absolute; right:10px; top:10px;
    display:inline-flex; align-items:center; justify-content:center;
    width:34px; height:34px; border-radius:999px; cursor:pointer;
    border:1px solid rgba(255,255,255,.75);
    background: radial-gradient(110% 150% at 30% 0%, rgba(255,255,255,.35), rgba(255,255,255,.15)),
                var(--anni-accent);
    color:#fff; font-weight:900;
    box-shadow:0 6px 18px rgba(2,6,23,.22);
  }}

  .{uid}-body {{ padding:12px; }}
  .{uid}-img {{
    display:block; margin:0 auto;
    max-width:100%; max-height:68vh;  /* proportional & never too big */
    width:auto; height:auto; border-radius:12px;
    border:1px solid var(--anni-line); box-shadow:0 6px 20px rgba(2,6,23,.12);
    object-fit:contain;
  }}
</style>
<div class="{uid}-row">
  <input id="{uid}-toggle" type="checkbox" />
  <label for="{uid}-toggle" class="{uid}-pill">{label}</label>
  <div class="{uid}-modal" role="dialog" aria-modal="true">
    <label class="{uid}-backdrop" for="{uid}-toggle" aria-hidden="true"></label>
    <!-- FX layer -->
    <div class="{uid}-fx">
      <!-- lots of balloons -->
      <span class="{uid}-balloon" style="left:4%;  --bclr:#60a5fa; --spd:12s;"></span>
      <span class="{uid}-balloon" style="left:32%; --bclr:#f43f5e; --spd:10.5s;"></span>
      <span class="{uid}-balloon" style="left:48%; --bclr:#60a5fa; --spd:11.5s;"></span>
      <span class="{uid}-balloon" style="left:58%; --bclr:#22c55e; --spd:12.5s;"></span>
      <span class="{uid}-balloon" style="left:66%; --bclr:#f97316; --spd:10.8s;"></span>
      <span class="{uid}-balloon" style="left:74%; --bclr:#a78bfa; --spd:12.8s;"></span>
      <span class="{uid}-balloon" style="left:82%; --bclr:#f43f5e; --spd:11.2s;"></span>
      <span class="{uid}-balloon" style="left:90%; --bclr:#60a5fa; --spd:13.2s;"></span>
    </div>
    <!-- Card (no header text) -->
    <div class="{uid}-card">
      <label for="{uid}-toggle" class="{uid}-close" title="Close">✕</label>
      <div class="{uid}-body">
        <img class="{uid}-img" src="{data}" alt="CancerLab 13th anniversary">
      </div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )









def page_home():
# On the home page (where you want the CTA button to appear)
    show_anniversary_cta("static/anniversary13.jpg")
# img sem alterações
    hero_src = data_uri("hero_lab.jpg", mime="image/jpeg")
    left_img = data_uri("imghome1.jpg", mime="image/jpeg")
    right_img = data_uri("imghome2.jpg", mime="image/jpeg")
    landmarks_img = data_uri("landmarks.jpg", mime="image/jpeg")

    # map data (unchanged)
    lat = -15.767937821610321
    lon = -47.86710221994476
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
    show_help_widget(
    name="Victor Fleck",
    email="Victor.fleck906438@gmail.com",
    role="Undergraduate Pharmacy Student • Web Developer :) ",
    phone="+55 61 991281207",
    label="Problems with the website?"
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
                <p></p>
                <p></p>
                <div class="chips" aria-label="Funding and focus tags">
                  <span class="chip">NGS</span><span class="chip">digital PCR</span><span class="chip">ctDNA</span>
                  <span class="chip">CRC</span><span class="chip">Screening</span><span class="chip">Therapy monitoring</span>
                </div>
              </section>
              <section id="epigenetics" class="section" aria-labelledby="epigenetics-h">
                <h2 id="epigenetics-h">Cancer Epigenetics</h2>
                <p>Our laboratory investigates how epigenetic regulators, including protein methyltransferases and demethylases, influence the development and progression of solid tumors and leukemias. By studying their roles in gene regulation, chromatin organization, and genomic stability, we aim to uncover how their dysregulation drives cancer. We also seek to identify novel biomarkers and therapeutic targets, translating our findings into more precise and effective cancer treatments. We use a variety of approaches to investigate their association with carcinogenesis and to identify new prognostic markers and therapeutic targets. Our work highlights how the dysregulation of these enzymes are not just passive modifiers of the genome but active drivers of cancer biology, opening opportunities for more precise and effective treatments.</p>
                <div class="chips" aria-label="Funding and focus tags">
                  <span class="chip">Leukemias</span><span class="chip">Chromatin organization</span><span class="chip">Methyltransferases</span>
                </div>
              </section>
              <section id="gene-editing" class="section" aria-labelledby="gene-editing-h">
                <h2 id="gene-editing-h">CRISPR/Cas9 Gene Editing</h2>
                <p>CRISPR-Cas9 is a powerful technology that allows scientists to precisely modify DNA within living cells. It uses a guide RNA to locate a specific DNA sequence and the Cas9 enzyme to make a targeted cut at that location. This cut can then be repaired by the cell, allowing us to disable, modify, or insert genes. In this context, our group is actively to development CRISPR/Cas9-based Gene editing tools for selective knockout (KO) of cancer-related targets, with a primary focus on epigenetic modifiers. Although CRISPR is a relatively recent innovation in biotechnology, it has rapidly become an essential research tool. Nevertheless, optimizing and implementing this technology still requires significant effort, which can exceed the capacity of many research laboratories. Our laboratory aims to serve as a facilitator, making CRISPR accessible to other research groups through collaborative efforts or service provision. By bypassing the resource-intensive process of optimization, we provide practical, ready-to-use solutions for immediate applications, thereby contributing to the advancement of regional and national scientific research.</p>
                <div class="chips" aria-label="Funding and focus tags">
                  <span class="chip">KO</span><span class="chip">Cas9 nuclease</span><span class="chip">CRISPR/Cas9</span>
                  <span class="chip">Clonal isolation</span><span class="chip">Off-target analysis</span>
                </div>
                </section>
            </main>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def page_publications():
    """
    Publications + Patents (yearly sections, with sub-sections)
    - Journal/other publications and Patents are grouped by YEAR.
    - Inside each year, items are split into two blocks: “Publications” and “Patents”.
    - If a DOI is provided it’s used directly; otherwise we try Crossref; else fall back to Google Scholar.
    - New links you sent are included and open directly.
    """
    import html, urllib.parse, mimetypes, base64
    from collections import defaultdict
    from functools import lru_cache
    from pathlib import Path
    import streamlit as st

    # ---------- (OPTIONAL) DOI lookup via Crossref ----------
    try:
        import requests  # keep optional; code still works without it
    except Exception:
        requests = None

    # ---------- helpers ----------
    def _ext_icon_svg():
        return (
            '<span class="ext" aria-hidden="true"></span>'
        )

    @lru_cache(maxsize=256)
    def find_doi(title: str, journal: str = "", year: int | None = None) -> str | None:
        # Use provided DOI if we already cached it
        key = f"{journal.strip()}|{title.strip()}"
        if key in DOI_CACHE:
            return DOI_CACHE[key]
        if not requests:
            return None
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

    def _scholar_query_link(title: str, journal: str) -> str:
        q = urllib.parse.quote_plus((title + " " + journal).strip())
        return f"https://scholar.google.com/scholar?q={q}"

    def _google_patents_link(number_or_title: str) -> str:
        q = urllib.parse.quote_plus(number_or_title)
        return f"https://patents.google.com/?q={q}"

    # ---------- STYLE ----------
    st.markdown(
        """
        <style>
          .pub-wrap { max-width:1180px; margin:28px auto 40px; padding:0 16px; }

          .pub-h1   { font-weight:900; font-size:clamp(26px,3.6vw,38px); margin:6px 0 0; color:var(--TEXT_DARK,#0f172a); }
          .pub-sub  { color:#475569; font-size:.98rem; margin: 4px 0 18px; }

          /* year index chips */
          .year-index { display:flex; flex-wrap:wrap; gap:8px; margin: 12px 0 18px; }
          .year-chip {
            display:inline-block; padding:6px 10px; border:1px solid #e6e8ee; border-radius:999px;
            text-decoration:none; font-weight:700; font-size:.92rem; color:#0f172a; background:#fff;
          }
          .year-chip:hover { border-color:#cdd3e0; }

          /* year section */
          .year-section { margin: 26px 0 24px; scroll-margin-top: 90px; }
          .year-title {
            font-weight:900; font-size:clamp(18px,2.6vw,24px); color:#0f172a; margin:0 0 10px;
            display:flex; align-items:center; gap:10px;
          }
          .year-count {
            font-weight:700; color:#475569; font-size:.88rem; background:#f1f5f9; border:1px solid #e2e8f0;
            padding:2px 8px; border-radius:999px;
          }

          /* subsection headers (Publications / Patents) */
          .subhead {
            display:flex; align-items:center; gap:10px; margin: 10px 0 8px;
            font-weight:900; color:#0f172a; font-size: clamp(14px,1.8vw,18px);
          }
          .subhead .bar {
            height:3px; border-radius:2px; background:rgba(63,94,181,.35); flex:1;
          }

          /* common list + item card */
          .item-list { list-style:none; padding:0; margin:0; display:grid; gap:10px; }
          .item {
            background:#fff; border:1px solid #e6e8ee; border-radius:14px;
            padding:12px 14px; display:grid; grid-template-columns: 1fr auto; gap:10px; align-items:start;
            position:relative; overflow:hidden;
            transition: box-shadow .15s ease, border-color .15s ease, transform .15s ease;
          }
          .item:hover { box-shadow:0 8px 18px rgba(2,6,23,.08); border-color:#d9dde3; transform: translateY(-2px); }
          .item .lead { font-weight:800; color:var(--primary, #1351d8); text-decoration:none; }
          .item .lead:hover { text-decoration:underline; }
          .item .meta { color:#475569; font-size:.92rem; margin-top:4px; }
          .aside { display:flex; gap:8px; align-items:center; }

          .doi-badge, .link-badge {
            display:inline-flex; align-items:center; gap:6px;
            font-size:.78rem; padding:3px 9px; border-radius:999px;
            border:1px solid #cbd5e1; color:#334155; background:#f8fafc; text-decoration:none;
          }
          .doi-badge:hover, .link-badge:hover { border-color:#aab7c7; }

          .ext {
            display:inline-block; width:12px; height:12px;
            background: conic-gradient(from 90deg, #64748b, #94a3b8);
            -webkit-mask: url('data:image/svg+xml;utf8,<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path fill="black" d="M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42 9.3-9.29H14V3z"/><path fill="black" d="M5 5h5V3H3v7h2V5zm0 14v-5H3v7h7v-2H5z"/></svg>') center/contain no-repeat;
                    mask: url('data:image/svg+xml;utf8,<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path fill="black" d="M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42 9.3-9.29H14V3z"/><path fill="black" d="M5 5h5V3H3v7h2V5zm0 14v-5H3v7h7v-2H5z"/></svg>') center/contain no-repeat;
          }

          /* patent flair */
          .item.patent::before {
            content:""; position:absolute; left:0; top:0; bottom:0; width:3px;
            background: linear-gradient(#fde68a,#fca5a5);
          }
          .patent .meta { color:#475569; }

          .back-top { display:inline-block; margin:10px 0 0; font-size:.88rem; color:#0f172a; text-decoration:none; }
          .back-top:hover { text-decoration:underline; }
        </style>
        """, unsafe_allow_html=True
    )

    # ---------- DATA ----------
    PUBLICATIONS = [
        # Recent examples (your existing items)
        {"authors": "Lopes, M. A.; Cordeiro, M. E. R.; Barreto, F. A. T.; Moreno, L. S.; Silva, A. A. M.; Loyola, M. B.; Soares, M. V. A.; Sousa, J. B.; Pittella-Silva, F.",
         "title": "Assessment of cfDNA release dynamics during colorectal cancer surgery",
         "journal": "Oncotarget", "year": 2025},
        {"authors": "Hollanda, C. N.; Gualberto, A. C. M.; Motoyama, A. B.; Pittella-Silva, F.",
         "title": "Advancing Leukemia Management Through Liquid Biopsy: Insights into Biomarkers and Clinical Utility",
         "journal": "Cancers", "year": 2025},

        {"authors": "Olivera Santana, B. L.; De Loyola, M. B.; Gualberto, A. C. M.; Pittella-Silva, F.",
         "title": "Genetic Alterations of SMYD4 in Solid Tumors Using Integrative Multi-Platform Analysis",
         "journal": "International Journal of Molecular Sciences", "year": 2024},
        {"authors": "Gatto, C. C.; Cavalcante, C. de Q. O.; Lima, F. C.; Nascimento, É. C. M.; Martins, J. B. L.; Santana, B. L. O.; Gualberto, A. C. M.; Pittella-Silva, F.",
         "title": "Structural Design, Anticancer Evaluation, and Molecular Docking of Newly Synthesized Ni(II) Complexes with ONS-Donor Dithiocarbazate Ligands",
         "journal": "Molecules", "year": 2024},
        {"authors": "Silva-Carvalho, A. É.; Féliu-Braga, L. D. C.; Bogéa, G. M. R.; de Assis, A. J. B.; Pittella-Silva, F.; Saldanha-Araujo, F.",
         "title": "GLP and G9a histone methyltransferases as potential therapeutic targets for lymphoid neoplasms",
         "journal": "Cancer Cell International", "year": 2024},

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

        {"authors": "Pittella-Silva, F.",
         "title": "Targeting DNA Methylation as an Epigenetic Leukocyte Counting Tool",
         "journal": "Clinical Chemistry", "year": 2022},
        {"authors": "Watanabe, K.; Nakamura, T.; Kimura, Y.; Motoya, M.; Kojima, S.; Kuraya, T.; …; Pittella-Silva, F.; Nakamura, Y.; Low, A. S.",
         "title": "Tumor-informed approach improved ctDNA detection rate in resected pancreatic cancer",
         "journal": "International Journal of Molecular Sciences", "year": 2022},

        {"authors": "Silva, F. P.; Kimura, Y.; Low, S.-K.; Nakamura, Y.; Motoya, M.",
         "title": "Amplification of mutant in a patient with advanced metastatic pancreatic adenocarcinoma detected by liquid biopsy: A case report",
         "journal": "Molecular and Clinical Oncology", "year": 2021},

        {"authors": "Pittella-Silva, F.; Chin, Y. M.; Chan, H. T.; Nagayama, S.; Miyauchi, E.; Low, S.-K.; Nakamura, Y.",
         "title": "Plasma or Serum: Which Is Preferable for Mutation Detection in Liquid Biopsy?",
         "journal": "Clinical Chemistry", "year": 2020},

        # ---- NEW links you sent (years inferred from the urls) ----
        {"authors": "", "title": "Article (Spandidos – IJO)", "journal": "International Journal of Oncology",
         "year": 2013, "url": "https://www.spandidos-publications.com/10.3892/ijo.2013.1981",
         "doi": "10.3892/ijo.2013.1981"},
        {"authors": "", "title": "Article (ScienceDirect)", "journal": "",
         "year": 2014, "url": "https://www.sciencedirect.com/science/article/pii/S0145212614000319?via%3Dihub"},
        {"authors": "", "title": "Article (Spandidos – Oncol Rep.)", "journal": "Oncology Reports",
         "year": 2017, "url": "https://www.spandidos-publications.com/10.3892/or.2017.6022",
         "doi": "10.3892/or.2017.6022"},
        {"authors": "", "title": "Article (Wiley – Mediators of Inflammation)", "journal": "Mediators of Inflammation",
         "year": 2020, "url": "https://onlinelibrary.wiley.com/doi/10.1155/2020/7045217",
         "doi": "10.1155/2020/7045217"},
    ]

    # Optional DOI cache (speeds up lookups or overrides)
    DOI_CACHE = {
        "International Journal of Oncology|Article (Spandidos – IJO)": "10.3892/ijo.2013.1981",
        "Oncology Reports|Article (Spandidos – Oncol Rep.)": "10.3892/or.2017.6022",
        "Mediators of Inflammation|Article (Wiley – Mediators of Inflammation)": "10.1155/2020/7045217",
    }

    # ---------- PATENTS ----------
    PATENTS = [
        {
            "year": 2013,
            "inventors": "SILVA, F. P. (PITTELLA-SILVA, F.); Gomes, A. D.; Lunardi, C. N.; Gomes, D. A.",
            "title": "Composição antitumoral à base de micro e nanopartículas poliméricas, seu processo de obtenção e suas aplicações",
            "jurisdiction": "Brazil (INPI)",
            "number": "BR102013017203",
            "deposited": "2013-07-04",
            "url": _google_patents_link("BR102013017203"),
        },
        {
            "year": 2015,
            "inventors": "LUO, M.; BLUM, G.; SANCHEZ, G. I.; YANG, L.; SILVA, F. P. (PITTELLA-SILVA, F.)",
            "title": "Naphthaquinone Methyltransferase Inhibitors and Uses Thereof",
            "jurisdiction": "WIPO (PCT)",
            "number": "WO/2015/172076",
            "deposited": "2015-08-05",
            "granted": "2015-12-11",
            "url": _google_patents_link("WO2015172076"),
        },
        {
            "year": 2015,
            "inventors": "LUO, M.; BLUM, G.; SANCHEZ, G. I.; SILVA, F. P. (PITTELLA-SILVA, F.)",
            "title": "Naphthaquinone Methyltransferase Inhibitors and Uses Thereof",
            "jurisdiction": "Canada (CIPO)",
            "number": "CA2946609",
            "deposited": "2015-12-11",
            "url": _google_patents_link("CA2946609"),
        },
        {
            "year": 2016,
            "inventors": "LUO, M.; BLUM, G.; SANCHEZ, G. I.; SILVA, F. P. (PITTELLA-SILVA, F.)",
            "title": "Naphthaquinone Methyltransferase Inhibitors and Uses Thereof",
            "jurisdiction": "Australia (IP Australia)",
            "number": "AU2015255692",
            "deposited": "2016-11-03",
            "url": _google_patents_link("AU2015255692"),
        },
        {
            "year": 2017,
            "inventors": "LUO, M.; BLUM, G.; SANCHEZ, G. I.; SILVA, F. P. (PITTELLA-SILVA, F.)",
            "title": "Naphthaquinone Methyltransferase Inhibitors and Uses Thereof",
            "jurisdiction": "Japan (JPO)",
            "number": "JP2017511562",
            "deposited": "2017-06-15",
            "url": _google_patents_link("JP2017511562"),
        },
        {
            "year": 2016,
            "inventors": "LUO, M.; WANG, J.; SILVA, F. P. (PITTELLA-SILVA, F.)",
            "title": "SET8 INHIBITORS AND USES THEREOF",
            "jurisdiction": "USA (USPTO)",
            "number": "US 62/287,263 (provisional)",
            "deposited": "2016-01-26",
            "url": _google_patents_link("62/287,263 SET8 inhibitors"),
        },
    ]

    # ---------- GROUP BY YEAR ----------
    pubs_by_year: dict[int, list[dict]] = defaultdict(list)
    pats_by_year: dict[int, list[dict]] = defaultdict(list)

    for p in PUBLICATIONS:
        pubs_by_year[int(p["year"])].append(p)
    for pt in PATENTS:
        pats_by_year[int(pt["year"])].append(pt)

    years = sorted(set(pubs_by_year.keys()) | set(pats_by_year.keys()), reverse=True)

    # ---------- RENDER ----------
    st.markdown('<div class="pub-wrap" id="top">', unsafe_allow_html=True)
    st.markdown('<div class="pub-h1">Publications</div>', unsafe_allow_html=True)
    st.markdown('<div class="pub-sub">Peer-reviewed articles and patents, grouped by year.</div>', unsafe_allow_html=True)

    # year index
    chips = [f'<a class="year-chip" href="#year-{y}">{y}</a>' for y in years]
    st.markdown(f'<nav class="year-index">{"".join(chips)}</nav>', unsafe_allow_html=True)

    # per-year sections
    for y in years:
        pub_items = pubs_by_year.get(y, [])
        pat_items = pats_by_year.get(y, [])

        st.markdown(f'<section class="year-section" id="year-{y}">', unsafe_allow_html=True)
        st.markdown(f'<div class="year-title">{y} '
                    f'<span class="year-count">{len(pub_items) + len(pat_items)}</span></div>', unsafe_allow_html=True)

        # ---- Publications
        if pub_items:
            st.markdown('<div class="subhead">Publications <span class="bar"></span></div>', unsafe_allow_html=True)
            st.markdown('<ul class="item-list">', unsafe_allow_html=True)
            for p in pub_items:
                title = (p.get("title") or "").strip()
                journal = (p.get("journal") or "").strip()
                authors = (p.get("authors") or "").strip()
                doi = (p.get("doi") or None)
                url = (p.get("url") or None)

                href = None
                badge_html = ""
                if doi:
                    href = f"https://doi.org/{urllib.parse.quote(doi, safe='/')}"
                    badge_html = f'<a class="doi-badge" href="{href}" target="_blank" rel="noopener">DOI {_ext_icon_svg()}</a>'
                elif url:
                    href = url
                    badge_html = f'<a class="link-badge" href="{html.escape(url)}" target="_blank" rel="noopener">Open {_ext_icon_svg()}</a>'
                else:
                    guess = find_doi(title, journal, y)
                    if guess:
                        href = f"https://doi.org/{urllib.parse.quote(guess, safe='/')}"
                        badge_html = f'<a class="doi-badge" href="{href}" target="_blank" rel="noopener">DOI {_ext_icon_svg()}</a>'
                    else:
                        href = _scholar_query_link(title, journal)
                        badge_html = f'<a class="link-badge" href="{href}" target="_blank" rel="noopener">Search {_ext_icon_svg()}</a>'

                meta_bits = []
                if authors: meta_bits.append(html.escape(authors))
                if journal: meta_bits.append(f"<i>{html.escape(journal)}</i>")
                meta = " · ".join(meta_bits)

                st.markdown(
                    f"""
                    <li class="item">
                      <div class="pub-main">
                        <a class="lead" href="{html.escape(href)}" target="_blank" rel="noopener">{html.escape(title)}</a>
                        {'<div class="meta">'+meta+'</div>' if meta else ''}
                      </div>
                      <div class="aside">{badge_html}</div>
                    </li>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown('</ul>', unsafe_allow_html=True)

        # ---- Patents
        if pat_items:
            st.markdown('<div class="subhead">Patents <span class="bar"></span></div>', unsafe_allow_html=True)
            st.markdown('<ul class="item-list">', unsafe_allow_html=True)
            for pt in pat_items:
                title = pt["title"]
                num = pt.get("number", "")
                jur = pt.get("jurisdiction", "")
                inv = pt.get("inventors", "")
                dep = pt.get("deposited", "")
                grant = pt.get("granted", "")
                url = pt.get("url") or _google_patents_link(f'{num} {title}')

                meta_bits = []
                if inv:  meta_bits.append(html.escape(inv))
                if jur:  meta_bits.append(html.escape(jur))
                if dep:  meta_bits.append(f"Deposit: {html.escape(dep)}")
                if grant: meta_bits.append(f"Grant: {html.escape(grant)}")
                meta = " · ".join(meta_bits)

                st.markdown(
                    f"""
                    <li class="item patent">
                      <div class="pub-main">
                        <a class="lead" href="{html.escape(url)}" target="_blank" rel="noopener">
                          {html.escape(title)} ({html.escape(num)})
                        </a>
                        {'<div class="meta">'+meta+'</div>' if meta else ''}
                      </div>
                      <div class="aside">
                        <a class="link-badge" href="{html.escape(url)}" target="_blank" rel="noopener">Open {_ext_icon_svg()}</a>
                      </div>
                    </li>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown('</ul>', unsafe_allow_html=True)

        st.markdown('<a class="back-top" href="#top">Back to top ↑</a>', unsafe_allow_html=True)
        st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def page_equipment():
    """
    Equipment page (no search bar)
    - Responsive card grid
    - Full-card click -> PNIPE equipment page in a new tab
    """
    import streamlit as st
    import html
    from textwrap import dedent

    # ====== DATA ======
    EQUIPMENT = [
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

    # ====== STYLES ======
    st.markdown(dedent("""
    <style>
      :root{
        --eq-ink: var(--TEXT_DARK, #0f172a);
        --eq-muted:#55637b;
        --eq-line:#e6e8ee;
        --eq-accent: var(--bar-bg, #3f5eb5);
        --eq-card:#fff;
      }
      .eq-wrap{ max-width:1180px; margin:0 auto; padding: 8px 16px 28px; }
      .eq-h1{ font-weight:900; font-size:clamp(24px,3.4vw,34px); color:var(--eq-ink); margin:18px 0 6px; }
      .eq-sub{ color:#4b5563; margin-bottom:14px; }

      .eq-grid{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:14px; }
      .eq-card{
        display:block; text-decoration:none; color:inherit;
        background:var(--eq-card);
        border:1px solid var(--eq-line); border-radius:14px; padding:14px;
        transition:transform .12s ease, box-shadow .12s ease, border-color .12s ease, background .12s ease;
        position:relative;
      }
      .eq-card::before{
        content:""; position:absolute; left:0; top:0; bottom:0; width:3px;
        background: linear-gradient(#bfdbfe,#93c5fd); border-radius:3px 0 0 3px; opacity:.8;
      }
      .eq-card:hover{
        transform:translateY(-2px); box-shadow:0 10px 18px rgba(2,6,23,.08); border-color:#d9dde3; background:#ffffff;
      }
      .eq-title{ font-weight:900; color:var(--eq-ink); line-height:1.18; }
      .eq-func{ color:var(--eq-muted); font-size:.92rem; margin-top:4px; }

      .eq-open{
        display:inline-flex; gap:6px; align-items:center; margin-top:10px;
        font-size:.86rem; color:var(--eq-accent); font-weight:800;
      }
      .eq-open .ext{
        width:12px; height:12px; display:inline-block; background: currentColor;
        -webkit-mask:url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="black" d="M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42 9.3-9.29H14V3z"/><path fill="black" d="M5 5h5V3H3v7h2V5zm0 14v-5H3v7h7v-2H5z"/></svg>') center/contain no-repeat;
                mask:url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="black" d="M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42 9.3-9.29H14V3z"/><path fill="black" d="M5 5h5V3H3v7h2V5zm0 14v-5H3v7h7v-2H5z"/></svg>') center/contain no-repeat;
      }
      .eq-card:focus{ outline:none; box-shadow:0 0 0 3px rgba(59,130,246,.35); }
    </style>
    """), unsafe_allow_html=True)

    # ====== RENDER ======
    st.markdown('<div class="eq-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="eq-h1">Equipment</div>', unsafe_allow_html=True)
    st.markdown('<div class="eq-sub">Click any card to open the PNIPE equipment page.</div>', unsafe_allow_html=True)

    cards = ['<div class="eq-grid">']
    for it in EQUIPMENT:
        name = html.escape(it["name"])
        fn   = html.escape(it.get("function",""))
        url  = html.escape(it["url"])
        cards.append(dedent(f"""
        <a class="eq-card" href="{url}" target="_blank" rel="noopener noreferrer" tabindex="0" aria-label="{name}">
          <div class="eq-title">{name}</div>
          {f'<div class="eq-func">{fn}</div>' if fn else ''}
          <div class="eq-open"><span class="ext" aria-hidden="true"></span> Open on PNIPE</div>
        </a>
        """).strip())
    cards.append("</div>")
    st.markdown("".join(cards), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)



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
        {"name": "Larissa Fernanda Campos Moreira da Silva, MD", "role": "Clinical Oncologist • PhD Student",
            "photo": "larissa.jpg", "bio": "Graduated in Medicine from the Federal University of the State of Rio de Janeiro (2003), with residencies in Internal Medicine and Medical Oncology. Currently heads the Oncology Department at the Brasília Military Area Hospital, with managerial and attending responsibilities. Leads the lung-cancer screening project across military hospitals in the Federal District and serves as regional lead for Clinical Oncology in military hospitals of Brazil’s Midwest. Serves on the Brazilian Army’s Technical Chamber of Oncology, with responsibility for breast, skin, and tumor-agnostic indications. Practices as a medical oncologist at Oncologia Alvorada (Américas group). From 2020 to June 2025, served at Oncologia Santa Marta as medical coordinator, leading care pathways and the lung-cancer screening protocol. Pursuing a PhD in Medical Sciences (oncology and molecular biology applied to medicine) at the University of Brasília. Thesis: “Plasma expression of miRNAs: miRNA-145-5p, miRNA-145-3p2, miRNA-155, miR-21, miR-10b, and let-7 in patients with breast cancer. Established three infusion centers: two military (Military Area Hospital of Recife and Military Area Hospital of Brasília) and one civilian intra-hospital center at Hospital Santa Marta (Oncologia Santa Marta). Previous experience includes attending physician at Hospital Rios D’or, preceptor for the Internal Medicine residency at Santa Casa de Misericórdia de Campo Grande, faculty in Medical Skills at the University for the Development of the State and the Pantanal Region, and clinical roles at the Brazilian Army Central Hospital and other oncology reference institutions. Extensive background in service management, creation of infusion centers, clinical research, implementation of care pathways, and delivery of both outpatient and inpatient oncology care.",
            "degrees": ["PhD Candidate in Medical Sciences, University of Brasília (2022–present)",
                        "Master's Candidate in Medical Sciences, University of Brasília (2022–present)",
                        "Medical Residency in Internal Medicine, UNIRIO (2004)",
                        "Specialization in Military Sciences (Officer Improvement Course), ESAO (2020–2021)",
                        "Postgraduate Specialization in Clinical Oncology, Hospital Central do Exército (2013–2016)",
                        "Lato Sensu Postgraduate in Military Sciences, Escola de Saúde do Exército (2011)",
                        "MD (Medicine), UNIRIO (1997–2003) "], "email": "", "institution": "University of Brasília",
        "lattes": "http://lattes.cnpq.br/2380982097052834", "orcid": "https://orcid.org/0000-0001-5896-7204"},
           {"name": "Ísis de Araujo Oliveira Nakashoji, MSc", "role": "PhD Student",
            "photo": "isi.jpg", "bio": "Holds a B.Sc. in Pharmacy (University of Brasília, 2018), a Specialization in Clinical Analysis and an M.Sc. in Medical Sciences (University of Brasília, 2021). Currently a PhD candidate in Medical Sciences at the University of Brasília, evaluating the impact of HPV vaccination among women treated in Brazil’s public health system (SUS). Works as a biochemical pharmacist with the Federal District Health Department, in hospital pharmacy. Experience spans Molecular Biology, Cytopathology, Cancer Cells, Immunohistochemistry, and Hospital Pharmacy.",
            "degrees": ["PhD Candidate in Medical Sciences, University of Brasília (2021–present)",
                        "M.Sc. in Medical Sciences, University of Brasília (2019–2021)",
                        "Lato Sensu Postgraduate Specialization in Traditional Chinese Medicine, Curante Cursos Educacional (2022–2024)",
                        "Specialization in Clinical Analysis, Universidade Paulista – UNIP (2019)",
                        "B.Sc. in Pharmacy, University of Brasília (2014–2018)"], "email": "", "institution": "University of Brasília",
            "lattes": "http://lattes.cnpq.br/1743833485792512", "orcid": "https://orcid.org/0000-0002-9303-1169"},
           {"name": "Lara De Souza Moreno, MD", "role": "Radiologist • MSc Student",
            "photo": "lara.jpg", "bio": "Holds a medical degree from the Catholic University of Brasília (2020). Residency in Radiology and Diagnostic Imaging at the University Hospital of Brasília (2025). Master’s in Medical Sciences from the University of Brasília (2024). Internal Medicine fellow at the DFSTAR Radiology Service – Rede D’Or.",
            "degrees": ["Master’s Candidate in Medical Sciences, University of Brasília (2024–present)",
                        "Medical Residency in Radiology and Diagnostic Imaging, University Hospital of Brasília / Ebserh (2022–2025)",
                        "Fellowship in Radiology and Diagnostic Imaging (Internal Medicine), Hospital DF Star – Rede D’Or (2025–present)",
                        "M.D., Catholic University of Brasília (2014–2020)"], "email": "larasmoreno@gmail.com", "institution": "University of Brasília",
            "lattes": "http://lattes.cnpq.br/4568437840946460", "orcid": "https://orcid.org/0009-0002-3390-4551"},
           {"name": "Debora Rodrigues Silveira, B.Pharm", "role": "MSc Student",
            "photo": "dbr.jpg", "bio": "Bachelor in Pharmaceutical Sciences from the University of Brasília (UnB), with experience in clinical research and cancer molecular genetics, plus internships across multiple levels of healthcare. Professional experience at ANVISA and participation in outreach projects and academic events, developing skills in health surveillance, health education, and scientific organization. Training is complemented by courses in pharmacotherapy, public policy, and public health. Interests include research, innovation, and qualified practice in biomedical sciences, genetics, and molecular biology.",
            "degrees": ["M.Sc. Candidate in Medical Sciences, University of Brasília (2025–present)",
                "B.Sc. in Pharmaceutical Sciences, University of Brasília (2018–2024)"], "email": "", "institution": "University of Brasília",
            "lattes": "http://lattes.cnpq.br/5490962025847708", "orcid": ""},
        
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
           
           {"name": "Augusto Silva Alves", "role": "Undergraduate Student",
         "photo": "ab.jpg", "bio": "Medical student at the University of Brasília (UnB), Brazil. Scientific initiation scholarship holder at UnB.",
         "degrees": ["MD Candidate (Medicine), University of Brasília (2022–present)"], "email": "", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/1220931705760601", "orcid": "https://orcid.org/0009-0005-6099-3889"},
           
           {"name": "Ângelo Antônio Silva Lima", "role": "Undergraduate Student",
         "photo": "as.jpg", "bio": "Medical student at the University of Brasília (UnB), Brazil.",
         "degrees": ["MD Candidate (Medicine), University of Brasília (2022–present)"], "email": "", "institution": "University of Brasília",
         "lattes": "http://lattes.cnpq.br/8940572165307881", "orcid": ""},
    
    
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
    show_help_widget(
    name="Victor Fleck",
    email="Victor.fleck906438@gmail.com",
    role="Undergraduate Pharmacy Student • Web Developer :) ",
    phone="+55 61 991281207",
    label="Problems with the website?"
    )

    



def page_partners():
    """
    Partners (labs/hospitals) + Funding (logo wall)
    - Put partner logos in:   static/partners/
    - Put funding logos in:   static/funding/
    - Partners show name, link, summary, country
    - Funding shows ONLY images (clickable if you add links in FUNDING_LINKS)
    """
    import streamlit as st
    from html import escape
    from pathlib import Path
    import mimetypes, base64
    from textwrap import dedent

    WRAP_MAX = 1180
    BASE_DIR = Path(__file__).parent / "static"
    PARTNER_DIR = BASE_DIR / "partners"
    FUNDING_DIR = BASE_DIR / "funding"

    # ---------- helpers ----------
    def _data_uri(p: Path) -> str:
        mime = mimetypes.guess_type(str(p))[0] or "image/png"
        return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"

    def _img_src(folder: Path, filename: str | None) -> str | None:
        if not filename:
            return None
        p = folder / filename
        return _data_uri(p) if p.exists() else None

    # ---------- PARTNERS: labs & hospitals only ----------
    PARTNERS = [
        {
            "name": "Cancer Institute of the State of São Paulo (ICESP)",
            "website": "https://icesp.org.br/cto/",
            "logo": "icesp.jpg",
            "country": "Brazil",
            "summary": "Translational oncology hub with advanced core facilities, biobank and research groups",
        },
        {
            "name": "Green Nanotechnology Laboratory (NaVe)",
            "website": "https://nanotecnologiaverde.complexonano.com/sobre-nos/",
            "logo": "nave.jpg",
            "country": "UnB – Brazil",
            "summary": "Multi-user lab focused on nanomaterials and nanosystems for health and environment",
        },
        {
            "name": "i.rad.Particles",
            "website": "https://i-rad-particles.com/#home",
            "logo": "rdp.jpg",
            "country": "Brazil",
            "summary": "Deep-tech company in energy and medical biotech; nanoparticle diagnostics and therapies",
        },
        {
            "name": "Laboratory for the Development of Nanostructured Systems (LDNano)",
            "website": "https://www2.ufjf.br/ldnano/",
            "logo": "ldnano.jpg",
            "country": "UFJF – Brazil",
            "summary": "Nanotechnology-based drug delivery to tune pharmacological properties",
        },
        {
            "name": "Biometals Lab Metal Biochemistry, Chemical Biology & Oxidative Stress",
            "website": "https://pnipe.mcti.gov.br/laboratory/23798",
            "logo": "biom.jpg",
            "country": "UFABC – Brazil",
            "summary": "Biochemistry and bioinorganic chemistry of trace metals in biology",
        },
        {
            "name": "Jan Grimm Lab",
            "website": "https://www.mskcc.org/research/ski",
            "logo": "msk.jpg",
            "country": "SKI – USA",
            "summary": "Imaging-driven nanomedicine for cancer: nanoparticles for therapy, Cerenkov/optoacoustic imaging, and PSMA biology",
        },
        {
            "name": "Children's Hospital of Brasília José Alencar",
            "website": "https://www.hcb.org.br/",
            "logo": "hcb.jpg",
            "country": "Brazil",
            "summary": "Public pediatric hospital providing medium- and high-complexity care (oncology, transplants, imaging), integrating care, teaching, and research",
        }

    ]

    # ---------- FUNDING: logo-only wall ----------
    # Put your funders' logos (svg/png/jpg/webp) in static/funding/
    # (Optional) map a logo filename to an external link here:
    FUNDING_LINKS = {
         "cnpq.jpg": "https://www.gov.br/cnpq/pt-br",
         "fapdf.jpg": "https://www.fap.df.gov.br/",
         "decit.jpg": "https://www.gov.br/saude/pt-br/composicao/sectics/decit",
         "capes.svg": "https://www.gov.br/capes/pt-br",
    }

    # If the folder has files, show what’s in it. Otherwise show nothing.
    def _discover_funding():
        if not FUNDING_DIR.exists():
            return []
        logos = []
        for p in sorted(FUNDING_DIR.iterdir()):
            if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
                logos.append({"file": p.name, "src": _data_uri(p), "href": FUNDING_LINKS.get(p.name)})
        return logos

    FUNDERS = _discover_funding()

    # ---------- styles ----------
    st.markdown(
        f"""
        <style>
          :root {{
            --ink: var(--TEXT_DARK, #0f172a);
            --muted:#4b5563;
            --line:#e6e8ee;
            --card:#ffffff;
          }}
          .partners-wrap {{ max-width:{WRAP_MAX}px; margin:0 auto; padding:0 16px 32px; }}
          .page-title {{
            font-size: clamp(26px,3.5vw,38px); font-weight:900; color:var(--ink);
            margin: 18px 0 6px; text-align:left;
          }}
          .section {{ margin: 18px 0 28px; scroll-margin-top:90px; }}
          .section-title {{
            font-size: clamp(18px,2.6vw,24px); font-weight:900; color:var(--ink);
            margin: 4px 0 14px; display:flex; align-items:center; gap:10px;
          }}
          .section-title::after {{
            content:""; flex:1; height:3px; border-radius:2px; background:rgba(63,94,181,.35);
          }}
          /* partner cards */
          .grid-partners {{
            display:grid; grid-template-columns:repeat(auto-fit, minmax(280px,1fr)); gap:18px;
          }}
          .p-card {{
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 16px;
            display:grid; grid-template-rows:auto auto 1fr auto; gap:10px;
            transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
          }}
          .p-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 26px rgba(2,6,23,.08);
            border-color:#d8dce6;
          }}
          .p-logo {{
            height: 64px; width: 100%; display:flex; align-items:center; justify-content:center;
            border-radius: 12px; background:#fff; border:1px solid var(--line);
            overflow:hidden;
          }}
          .p-logo img {{ max-height:56px; width:auto; object-fit:contain; display:block; }}
          .p-name a {{ color:#0f3bdc; font-weight:900; text-decoration:none; }}
          .p-name a:hover {{ text-decoration:underline; }}
          .p-summary {{ color:var(--muted); line-height:1.45; font-size:.95rem; }}
          .p-badge {{ display:inline-block; padding:4px 10px; border-radius:999px;
                     border:1px solid #cbd5e1; background:#f8fafc; color:#334155; font-size:.8rem; }}
          /* funding wall (logo-only) */
          .grid-funding {{
            display:grid; grid-template-columns:repeat(auto-fit, minmax(140px,1fr)); gap:14px;
          }}
          .fund-tile {{
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 14px;
            height: 92px;
            display:flex; align-items:center; justify-content:center;
            transition: transform .15s ease, box-shadow .15s ease, filter .15s ease, border-color .15s ease;
            filter: grayscale(22%);
          }}
          .fund-tile:hover {{
            transform: translateY(-3px);
            filter: grayscale(0%);
            box-shadow: 0 10px 22px rgba(2,6,23,.08);
            border-color:#d8dce6;
          }}
          .fund-tile img {{ max-height:64px; width:auto; object-fit:contain; display:block; }}
          @media (max-width:760px){{
            .p-logo {{ height: 60px; }}
            .p-logo img {{ max-height:52px; }}
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---------- small render helpers ----------
    def _partner_cards(items: list[dict]) -> str:
        blocks = ['<div class="grid-partners">']
        for it in items:
            name = escape(it.get("name", ""))
            url = (it.get("website") or "").strip()
            summary = escape(it.get("summary", ""))
            country = escape(it.get("country", ""))
            logo_src = _img_src(PARTNER_DIR, it.get("logo"))
            logo_html = (
                f'<div class="p-logo"><img src="{logo_src}" alt="{name} logo"></div>'
                if logo_src else
                f'<div class="p-logo"><span style="font-weight:800;color:#9aa3af">{name[:2]}</span></div>'
            )
            title_html = f'<a href="{escape(url)}" target="_blank" rel="noopener">{name}</a>' if url else name
            summary_html = f'<div class="p-summary">{summary}</div>' if summary else ""
            country_html = f'<div class="p-badge">{country}</div>' if country else ""
            blocks.append(dedent(f"""
              <article class="p-card">
                {logo_html}
                <div class="p-name">{title_html}</div>
                {summary_html}
                {country_html}
              </article>
            """).strip())
        blocks.append("</div>")
        return "".join(blocks)

    def _funding_wall(items: list[dict]) -> str:
        if not items:
            return '<div style="color:#64748b">Add funder logos to <code>static/funding/</code> to show them here.</div>'
        tiles = ['<div class="grid-funding">']
        for it in items:
            img = it["src"]; alt = escape(it["file"])
            if it.get("href"):
                tiles.append(f'<a class="fund-tile" href="{escape(it["href"])}" target="_blank" rel="noopener"><img src="{img}" alt="{alt}"></a>')
            else:
                tiles.append(f'<div class="fund-tile"><img src="{img}" alt="{alt}"></div>')
        tiles.append("</div>")
        return "".join(tiles)

    # ---------- render ----------
    st.markdown('<div class="partners-wrap">', unsafe_allow_html=True)

    st.markdown('<div class="page-title">Partners</div>', unsafe_allow_html=True)
    st.markdown(_partner_cards(PARTNERS), unsafe_allow_html=True)

    st.markdown('<section class="section" id="funding">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Funding</div>', unsafe_allow_html=True)
    st.markdown(_funding_wall(FUNDERS), unsafe_allow_html=True)
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
show_lab_header(
    image_relpath="static/imgfront",
    address_lines=[
        "Laboratory of Molecular Pathology of Cancer",
        "Faculty of Health Sciences",
        "University of Brasília",
        "Brasília – DF – Brazil",
    ],
)
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
         "equipment": page_equipment,
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

    








