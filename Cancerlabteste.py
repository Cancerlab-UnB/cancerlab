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

APP_BASE_URL = os.getenv("APP_BASE_URL", "https://cancerlab.up.railway.app")
SMTP_HOST    = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT    = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER    = (os.getenv("SMTP_USER") or "").strip()
SMTP_PASS    = (os.getenv("SMTP_PASS") or "").replace(" ", "").strip()
FROM_EMAIL   = SMTP_USER


# --- Configuração da Página ---
st.set_page_config(page_title="Banco de Dados - Cancer Lab", layout="centered")

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

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("cancerlabimg.png", width=225) 
st.markdown("""
<style>
.header-lab {
    text-align: center;
    margin-top: 0.1rem;
    margin-bottom: 2.0rem;
    max-width: 950px;   /* Aumente para deixar o texto mais largo */
    margin-left: auto;
    margin-right: auto;
}
.header-lab-text {
    font-size: 2.6rem;  /* Tamanho da fonte */
    color: #33b6ea;
    font-weight: 800;
    line-height: 1.13;
    letter-spacing: 0.5px;
    text-shadow: 0 2px 18px #005a9035;
    display: block;
}
@media (max-width: 800px) {
    .header-lab {
        max-width: 99vw;
    }
    .header-lab-text {
        font-size: 1.3rem;
    }
}
</style>
<div class="header-lab">
    <span class="header-lab-text">
        CancerLab – Laboratório de Patologia Molecular do Câncer
    </span>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* ===== Paleta (ajuste aqui os tons, se necessário) ===== */
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
      color: var(--text) !important;   /* usa #111827 do seu :root */
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
    CPF = st.text_input("CPF")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = autentica(CPF, senha)
        if user:
            st.session_state.usuario_logado = user
            st.markdown(
       f"<h3 style='color:#005A90; font-weight:700;'>Bem-vindo, {user['nome']}!</h3>",
       unsafe_allow_html=True
   )
            st.session_state.page = "index"
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")
    # 🔹 ADD – link 
    st.markdown(
        """
        <div style="margin-top: -0.5rem; margin-bottom: 0.5rem;">
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
    def deletar_paciente(paciente_id: str):
        # aqui você coloca a lógica real de exclusão (delete no DB, API, etc.)
        st.success(f"Paciente {paciente_id} removido com sucesso.")
    
    def ui_botao_remover(paciente_id: str, nome: str, key_prefix: str = ""):
        flag_key = f"{key_prefix}confirm_{paciente_id}"
        if flag_key not in st.session_state:
            st.session_state[flag_key] = False
    
        st.markdown("""
        <style>
          .tiny-danger button {
            padding:.25rem .6rem;font-size:.8rem;border-radius:6px;
            background:#FFF1F2;color:#7F1D1D;border:1px solid #FECACA;}
          .tiny-danger button:hover {background:#FFE4E6}
        </style>
        """, unsafe_allow_html=True)
    
        col = st.columns([1, 5])[0]
        with col:
            if st.button("Remover", key=f"{key_prefix}rm_{paciente_id}"):
                st.session_state[flag_key] = True
            st.markdown('<div class="tiny-danger"></div>', unsafe_allow_html=True)
    
        if st.session_state[flag_key]:
            st.warning(f"Remover **{nome}**? Essa ação é irreversível.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🗑️ Confirmar remoção", key=f"{key_prefix}yes_{paciente_id}"):
                    deletar_paciente(paciente_id)
                    st.session_state[flag_key] = False
                    st.experimental_rerun()
            with c2:
                if st.button("Cancelar", key=f"{key_prefix}no_{paciente_id}"):
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

    








