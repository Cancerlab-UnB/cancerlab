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

# ====================== Public Page inicio ======================
PRIMARY_BLUE = "#4E78C5"   # ajuste de cor 
TEXT_DARK = "#1b1f24"

# slug -> menu central 
PAGES_PUBLIC = [
    ("home", "home"),
    ("research", "research"),
    ("publications", "publications"),
    ("people", "people"),  
    ("partners", "partner labs"),
    ("login", "Internal Access"),
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
    LOGO_BASE = "cancerlablogoinicio"  # no extension here
    LOGO_EXT  = "jpg"
    logo_src = f"{LOGO_BASE}.{LOGO_EXT}"
    
    
    st.markdown(
        f"""
        <style>
          .topbar {{
            position: sticky; top: 0; z-index: 1000;
            background: {PRIMARY_BLUE};
            border-bottom: 1px solid rgba(0,0,0,.08);
          }}
          .topbar-inner {{
            max-width: 1180px; margin: 0 auto; padding: 10px 16px;
            display: grid; grid-template-columns: 1fr auto 1fr; align-items: center;
          }}
          .brand {{ display:flex; align-items:center; gap:10px; }}
          .brand img {{ height: 45px; width:auto; display:block; }}
          .brand small {{ color: white; opacity: .9; line-height:1.1; }}
          .menu {{ display:flex; gap:18px; align-items:center; justify-content:center; }}
          .menu a {{
            text-decoration:none; color:white; text-transform: lowercase;
            padding: 6px 10px; border-radius: 8px; font-weight:600;
          }}
          .menu a.active {{ background: rgba(255,255,255,.18); }}
          .icons {{ display:flex; gap:8px; align-items:center; justify-content:flex-end; }}
          .icon-btn {{
            background:transparent; border:1px solid rgba(255,255,255,.55);
            color:white; border-radius:8px; padding:6px 10px; font-weight:700;
            text-decoration:none;
          }}
          .icon-btn:hover {{ background: rgba(255,255,255,.14); }}
        </style>
        <div class="topbar">
          <div class="topbar-inner">
            <div class="brand">
              <img src="{logo_src}" alt="CancerLab"/>
              <small>Laboratory of Molecular Pathology of Cancer
              <br>University of Brasília</small>
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
    st.markdown(
        f"""
        <style>
          .wrap {{ max-width: 1180px; margin: 24px auto; padding: 0 16px; }}
          .hero {{ display:grid; grid-template-columns: 1.1fr .9fr; gap: 28px; align-items:start; }}
          @media (max-width: 980px) {{ .hero {{ grid-template-columns:1fr; }} }}
          .title {{ font-size: clamp(28px, 4.2vw, 44px); font-weight:800; color:{TEXT_DARK}; margin: 8px 0; }}
          .lead {{ color:#444; line-height:1.7; font-size: 17px; }}
          .imgframe {{ border:1px solid #e7e7e7; border-radius:6px; overflow:hidden; }}
          .divider {{ height:1px; background:#e8e8e8; margin:22px 0; }}
        </style>
        <div class="wrap">
          <div class="hero">
            <div>
              <div class="title">CancerLab — Laboratory of Molecular Pathology of Cancer</div>
              <p class="lead">
                (em branco.)
              </p>
              <div class="divider"></div>
              <p class="lead"><b>Note:</b> colocar aqui qualquer observação.</p>
            </div>
            <div class="imgframe">
              <img src="hero_lab.jpg" style="width:100%; display:block;" alt="UnB"/>
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
    st.markdown("## Publications\nThis page is under construction.")
    st.info("ta em branco .")

def page_people():
    import os
    import streamlit as st

    PEOPLE = [
        {
            "name": "Fábio Pittella Silva, PhD",
            "role": "Coordinator",
            "bio": (
                "Coordinator of the Cancer Molecular Pathology Laboratory at the University of Brasília. "
                "PhD (2008) and MSc (2004) in Molecular Pathology, Human Genome Center, University of Tokyo; "
                "BSc in Pharmacy and Biochemistry, Federal University of Juiz de Fora (2001). At the University of Tokyo, "
                "identified and described the genes WDRPUH, TIPUH1, and SMYD3, the first methyltransferase implicated in "
                "human carcinogenesis. Professor at UnB since 2008, supervising master’s, doctoral, and postdoctoral students. "
                "Associate researcher at the Cancer Precision Medicine Center, JFCR (Tokyo, since 2018), and visiting professor at "
                "Memorial Sloan-Kettering Cancer Center, New York (2014–2018), developing methyltransferase inhibitors. "
                "Expertise in molecular genetics, biochemistry, and cancer epigenetics, with focus on methyltransferases, "
                "liquid biopsy, and molecular targets for cancer diagnosis and therapy."
            ),
            "degrees": [
                "BSc in Pharmacy and Biochemistry, Federal University of Juiz de Fora (2001)",
                "MSc in Medical Sciences, University of Tokyo (2004)",
                "PhD in Molecular Pathology, University of Tokyo Human Genome Center (2008)",
            ],
            "email": "pittella@unb.br",
            "institution": "University of Brasília (UnB)",
            "lattes": "http://lattes.cnpq.br/4961976945101495",
            "orcid": "https://orcid.org/0000-0000-0000-0000",
            "photo": "fabio.jpg",
        },
        {
            "name": "Andrea Barretto Motoyama, PhD",
            "role": "Associate Professor",
            "bio": (
                "Associate Professor at the Department of Pharmacy, University of Brasília. "
                "PhD in Biochemistry, University of Basel (2002). Postdoctoral fellow at The Scripps Research Institute "
                "and The Burnham Institute, focusing on RNA stability and adhesion proteins/small GTPases. "
                "Expertise in cellular biology, biochemistry, molecular biology, oncology, and pharmacology."
            ),
            "degrees": [
                "BSc in Biological Sciences, University of Brasília (1997)",
                "PhD in Biochemistry, University of Basel, Switzerland (2002)",
                "Postdoctoral Fellow, The Scripps Research Institute (La Jolla, USA)",
                "Postdoctoral Fellow, The Burnham Institute for Medical Research (La Jolla, USA)",
            ],
            "email": "andreabm@unb.br",
            "institution": "UnB",
            "lattes": "http://lattes.cnpq.br/6229434599232057",
            "orcid": "",
            "photo": "andrea.jpg",
        },
        {
            "name": "Ana Cristina Moura Gualberto, PhD",
            "role": "Postdoctoral Researcher",
            "bio": (
                "PhD in Biological Sciences from the Federal University of Juiz de Fora (2019), investigating the role of "
                "matrix metalloproteinase silencing by RNA interference in breast cancer progression. Postdoctoral fellow at "
                "UFJF (2019–2022) studying adipose tissue exosomes in breast cancer. Currently a postdoctoral researcher at "
                "the University of Brasília, working on CRISPR/Cas9-based genome editing in cancer."
            ),
            "degrees": [
                "PhD in Biological Sciences, Federal University of Juiz de Fora (2019)",
                "Postdoctoral Fellow, Federal University of Juiz de Fora (2019–2022)",
                "Postdoctoral Researcher, University of Brasília (current)",
            ],
            "email": "",
            "institution": "UnB",
            "lattes": "http://lattes.cnpq.br/6338541953564765",
            "orcid": "",
            "photo": "anagualberto.jpg",
        },
        {
            "name": "Luis Janssen Maia, PhD",
            "role": "Researcher",
            "bio": (
                "BSc in Biological Sciences and MSc/PhD in Molecular Biology (UnB). Focus on microbiology and molecular "
                "biology, especially NGS to study viral/bacterial diversity and evolution, liquid biopsy applications, and "
                "molecular studies."
            ),
            "degrees": [
                "BSc in Biological Sciences, University of Brasília",
                "MSc in Molecular Biology, University of Brasília",
                "PhD in Molecular Biology, University of Brasília",
            ],
            "email": "",
            "institution": "UnB",
            "lattes": "http://lattes.cnpq.br/7167611866112740",
            "orcid": "",
            "photo": "luisJ.jpg",
        },
        {
            "name": "Ekaly Ivoneth Porto Apangha",
            "role": "Oncology Pharmacist",
            "bio": (
                "Pharmacist (UnB), Specialist in Cancer Care (ESCS). Experienced in chemotherapy compounding, "
                "clinical/oncology pharmacy, hospital and community pharmacy."
            ),
            "degrees": [
                "BSc in Pharmacy, University of Brasília (UnB)",
                "Specialization in Cancer Care, Escola Superior de Ciências da Saúde (ESCS)",
            ],
            "email": "ekaly.apangha@unb.br",
            "institution": "UnB",
            "lattes": "http://lattes.cnpq.br/0622839652506358",
            "orcid": "",
            "photo": "ekaly.jpg",
        },
        {
            "name": "Matheus de Oliveira Andrade, MD",
            "role": "Clinical Oncologist • PhD Candidate",
            "bio": (
                "MD (UnB) with exchange at QMUL. Internal Medicine (HCFMRP-USP) and Clinical Oncology (ICESP-FMUSP). "
                "Clinical oncologist at Rede Américas (Brasília). PhD candidate at UnB focusing on liquid biopsy in "
                "colorectal cancer."
            ),
            "degrees": [
                "Exchange in Biomedical Sciences, Queen Mary University of London (QMUL)",
                "Internal Medicine, HCFMRP-USP",
                "Clinical Oncology, ICESP-FMUSP",
                "PhD Candidate in Medical Sciences, UnB",
            ],
            "email": "matheusandradeoncologia@gmail.com",
            "institution": "UnB",
            "lattes": "http://lattes.cnpq.br/3451033370311538",
            "orcid": "https://orcid.org/0000-0001-8922-2715",
            "photo": "matheusmd.jpg",
        },
        {
            "name": "Mayra Veloso Ayrimoraes Soares, MD",
            "role": "Radiologist • PhD Candidate",
            "bio": (
                "MD (UnB, 1999). Radiology Residency (HBDF, 2001–2003). Radiologist at Hospital Sírio-Libanês and "
                "Laboratório Exame/DASA-DF. Supervisor of the Radiology Residency (UnB). MBA in Health Management (FGV). "
                "PhD candidate (UnB)."
            ),
            "degrees": [
                "MD, University of Brasília (1999)",
                "Residency in Radiology and Diagnostic Imaging, HBDF (2001–2003)",
                "MBA in Health Management, FGV (Brasília)",
                "PhD Candidate in Medical Sciences, UnB (current)",
            ],
            "email": "mayra.veloso@unb.br",
            "institution": "UnB",
            "lattes": "http://lattes.cnpq.br/4358326060572502",
            "orcid": "https://orcid.org/0000-0003-0796-5123",
            "photo": "mayramd.jpg",
        },
        {
            "name": "Brunna Letícia Oliveira Santana",
            "role": "PhD Student",
            "bio": (
                "BSc in Biological Sciences (UNIP, 2019). MSc in Medical Sciences – cancer epigenetics (UnB, 2022–2024). "
                "PhD student (UnB) investigating lysine methyltransferase knockouts to identify biomarkers and therapeutic "
                "targets in acute lymphoblastic leukemia."
            ),
            "degrees": [
                "BSc in Biological Sciences, Universidade Paulista (2019)",
                "MSc in Medical Sciences – Cancer Epigenetics, UnB (2022–2024)",
                "PhD Student in Medical Sciences, UnB (current)",
            ],
            "email": "",
            "institution": "UnB",
            "lattes": "http://lattes.cnpq.br/5131211187661647",
            "orcid": "https://orcid.org/0000-0003-4402-8358",
            "photo": "",  # add when available
        },
    ]

    st.markdown("""
    <style>
      .person-card {display:flex;align-items:center;margin:12px 0;padding:8px;
                    border:1px solid #e5e7eb;border-radius:10px;background:#f9fafb;}
      .person-photo {width:90px;height:90px;object-fit:cover;border-radius:8px;margin-right:14px;
                     border:1px solid #d1d5db;background:#fff;}
      .person-info {flex:1;}
      .person-name {font-weight:600;font-size:1.05rem;}
      .person-role {color:#374151;font-size:0.9rem;}
    
      /* remove the divider/borders that streamlit puts on expanders */
      .streamlit-expander {
          border-top: none !important;
          border-bottom: none !important;
          box-shadow: none !important;
      }
      .streamlit-expanderHeader {
          border: none !important;
      }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## People")

    def img_exists(path: str) -> bool:
        try:
            return bool(path) and os.path.exists(path)
        except Exception:
            return False

    for p in PEOPLE:
        st.markdown('<div class="person-card">', unsafe_allow_html=True)

        if img_exists(p.get("photo", "")):
            st.markdown(f'<img class="person-photo" src="{p["photo"]}" alt="{p["name"]}">', unsafe_allow_html=True)
        else:
            st.markdown('<div class="person-photo" style="display:flex;align-items:center;justify-content:center;color:#9ca3af;">?</div>', unsafe_allow_html=True)

        st.markdown('<div class="person-info">', unsafe_allow_html=True)
        st.markdown(f'<div class="person-name">{p["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="person-role">{p["role"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Details inside expander
        with st.expander("See more"):
            if p.get("bio"):
                st.write(p["bio"])
            if p.get("degrees"):
                st.markdown("**Degrees**")
                st.write("\n".join([f"- {d}" for d in p["degrees"]]))
            links = []
            if p.get("lattes"): links.append(f"[Lattes]({p['lattes']})")
            if p.get("orcid"):  links.append(f"[ORCID]({p['orcid']})")
            if links: st.markdown("**Links:** " + " · ".join(links))
            contact = []
            if p.get("email"): contact.append(f"📧 {p['email']}")
            if p.get("institution"): contact.append(f"🏛️ {p['institution']}")
            if contact: st.markdown("**Contact:** " + " • ".join(contact))


def page_partners():
    st.markdown("## Partner labs\nThis page is under construction.")
    st.info("ta em branco.")

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



# Páginas públicas do site:
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
        CPF = st.text_input("CPF")
        senha = st.text_input("Senha", type="password")
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
        st.rerun()
        
    if st.button("Dados Clínicos CCR"):
        st.session_state.page = "clinicos"
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

    # Carrega planilha fixa somente aqui!
    if "df_biopsia" not in st.session_state:
        st.session_state.df_biopsia = pd.read_excel("Entrada e Acompanhamento de Pacientes Biópsia Líquida CCR.xlsx")
    df = st.session_state.df_biopsia

    def df_to_html_table(df):
        return df.to_html(escape=False, index=False)

    # Mostra tabela enxuta
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

    







