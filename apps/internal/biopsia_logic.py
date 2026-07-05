# apps/internal/biopsia_logic.py
# ---------------------------------------------------------------------------
# Lógica de negócio da página "Entrada e Acompanhamento de Pacientes –
# Biópsia Líquida CCR", portada 1:1 do app Streamlit (Cancerlabteste__5_.py).
#
# São funções PURAS (sem Streamlit) reutilizadas pela view Django:
#   • normalização de cabeçalhos / textos / identificadores CBL
#   • parsing de datas em qualquer formato (BR, ISO, serial Excel)
#   • classificação visual das células (coletado / auto / futuro / atrasado)
#   • automação BxL: preenche datas futuras a partir da data de cirurgia
#   • padronização do identificador ao retirar o paciente do estudo
# ---------------------------------------------------------------------------
import re
from datetime import datetime, date

try:
    import numpy as np
    import pandas as pd
    HAS_PANDAS = True
except Exception:  # pragma: no cover
    HAS_PANDAS = False


# =====================================================================
# Normalização de texto / cabeçalhos / CBL
# =====================================================================
def norm_header(s) -> str:
    if s is None:
        return ""
    s = str(s).replace("\n", " ").replace("\r", " ").strip()
    return re.sub(r"\s+", " ", s)


def norm_text(s) -> str:
    if s is None:
        return ""
    s = str(s).strip().lower()
    return re.sub(r"\s+", " ", s)


def normalize_cbl_text(raw) -> str:
    """'CBL 3 (exc)' -> 'CBL3'; mantém demais tokens colados/uppercase."""
    s = str(raw or "").strip()
    m = re.search(r"\bCBL\s*(\d+)\b", s, flags=re.IGNORECASE)
    if m:
        return f"CBL{int(m.group(1))}"
    return re.sub(r"\s+", "", s).upper()


def is_event_id(raw_id: str) -> bool:
    """Paciente retirado do estudo (exc / saiu / falecimento '+')."""
    low = norm_text(raw_id)
    raw = str(raw_id or "")
    return ("exc" in low) or ("saiu" in low) or ("+" in raw)


# =====================================================================
# Datas
# =====================================================================
_DATE_RE = re.compile(
    r"(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b)"
)


def _excel_serial_to_ts(x):
    try:
        if HAS_PANDAS and pd.isna(x):
            return None
        if isinstance(x, (int, float)) and -100000 < float(x) < 400000:
            return (pd.to_datetime("1899-12-30")
                    + pd.to_timedelta(int(float(x)), unit="D")).to_pydatetime()
    except Exception:
        pass
    return None


def parse_date_any(v):
    """Converte qualquer representação para datetime (00:00) ou None."""
    if v is None:
        return None
    try:
        if isinstance(v, float) and np.isnan(v):
            return None
    except Exception:
        pass

    try:
        if HAS_PANDAS and isinstance(v, (pd.Timestamp, datetime)):
            return pd.to_datetime(v).normalize().to_pydatetime()
    except Exception:
        pass

    ts = _excel_serial_to_ts(v)
    if ts:
        return ts.replace(hour=0, minute=0, second=0, microsecond=0)

    s = str(v).strip()
    m = _DATE_RE.search(s)
    if not m:
        return None

    token = m.group(1).replace(".", "/").replace("-", "/")
    parts = token.split("/")
    if len(parts) != 3:
        return None

    if len(parts[0]) == 4:
        yy, mm, dd = parts
    else:
        dd, mm, yy = parts

    if len(yy) == 2:
        y = int(yy)
        yy = str(2000 + y if y <= 30 else 1900 + y)

    try:
        return datetime(int(yy), int(mm), int(dd))
    except ValueError:
        return None


def fmt_br(d) -> str:
    if HAS_PANDAS and isinstance(d, (datetime, pd.Timestamp)):
        return d.strftime("%d/%m/%y")
    if isinstance(d, datetime):
        return d.strftime("%d/%m/%y")
    return d


def extract_date_str(val):
    if val is None:
        return None
    m = _DATE_RE.search(str(val))
    if not m:
        return None
    token = m.group(1).replace(".", "/").replace("-", "/")
    parts = token.split("/")
    if len(parts) != 3:
        return None
    if len(parts[0]) == 4:
        yy, mm, dd = parts
    else:
        dd, mm, yy = parts
    if len(yy) == 4:
        yy = yy[-2:]
    return f"{dd.zfill(2)}/{mm.zfill(2)}/{yy.zfill(2)}"


def auto_text(d: datetime) -> str:
    return f"{fmt_br(d)}".strip()


def add_months(dt, months):
    y = dt.year + (dt.month - 1 + months) // 12
    m = (dt.month - 1 + months) % 12 + 1
    d = min(dt.day, [
        31,
        29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28,
        31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    ][m - 1])
    return dt.replace(year=y, month=m, day=d, hour=0, minute=0, second=0, microsecond=0)


# =====================================================================
# Estado das células
# =====================================================================
def is_empty_cell(v) -> bool:
    if v is None:
        return True
    try:
        if isinstance(v, float) and np.isnan(v):
            return True
    except Exception:
        pass
    s = str(v).strip()
    return s == "" or s.lower() in {"nan", "none"}


def is_auto_cell(v) -> bool:
    if v is None:
        return False
    return re.search(r"\bAUTO\b", str(v).upper()) is not None


def is_blocked_for_date_logic(val) -> bool:
    if val is None:
        return True
    try:
        if HAS_PANDAS and pd.isna(val):
            return True
    except Exception:
        pass
    s = re.sub(r"\s+", " ", str(val).strip().lower())
    blocked_exact = {
        "", "-", "--", "nan", "none", "nc", "sp", "f",
        "na", "n/a", "sem cirurgia", "sem tumor",
    }
    blocked_contains = [
        "não coletado", "nao coletado", "cancelado",
        "sem cirurgia", "sem tumor",
    ]
    if s in blocked_exact:
        return True
    return any(x in s for x in blocked_contains)


def has_collected_tag(val) -> bool:
    if val is None:
        return False
    return bool(re.search(r"\(\s*coletado\s*\)", str(val), flags=re.IGNORECASE))


def cell_display(val):
    """Legado: célula que contém 'AUTO' é exibida apenas como a data extraída."""
    if is_auto_cell(val):
        ds = extract_date_str(val)
        return ds if ds else val
    return val


def cell_class(val) -> str:
    """
    Classe CSS de cada célula, replicando o realce do Streamlit:
      collected → coletado (preto/negrito)
      auto      → data automática (azul)
      future    → data futura (verde) = coleta a agendar
      overdue   → data passada não coletada (vermelho) = atrasada
    """
    if is_blocked_for_date_logic(val):
        return ""
    if has_collected_tag(val):
        return "c-collected"
    if is_auto_cell(val):
        return "c-auto"
    d = parse_date_any(val)
    if d:
        dd = d.date()
        today = date.today()
        if dd > today:
            return "c-future"
        if dd < today:
            return "c-overdue"
    return ""


# =====================================================================
# Colunas BxL / Cirurgia
# =====================================================================
OFFSETS_MESES = {2: 1, 3: 6, 4: 12, 5: 18, 6: 24, 7: 30, 8: 36}


def bxl_num(c) -> int:
    m = re.search(r"bxl\s*(\d+)", str(c).lower())
    return int(m.group(1)) if m else 0


def is_bxl_col(c) -> bool:
    return re.search(r"\bbxl\s*\d+\b", str(c), flags=re.IGNORECASE) is not None


def find_cirurgia_col(cols):
    for c in cols:
        nc = str(c).lower()
        if "cirurgia" in nc and "bx liquida" not in nc:
            return c
    return None


def build_sequencia(cols):
    """[(rótulo, coluna, offset_meses)] começando na CIRURGIA."""
    bxl_cols = sorted([c for c in cols if is_bxl_col(c)], key=bxl_num)
    cirurgia_col = find_cirurgia_col(cols)
    seq = []
    if cirurgia_col:
        seq.append(("CIRURGIA", cirurgia_col, 0))
    for c in bxl_cols:
        n = bxl_num(c)
        if 2 <= n <= 8:
            seq.append((f"BxL {n}", c, OFFSETS_MESES.get(n)))
    return seq, cirurgia_col, bxl_cols


def grade_alvo(row, cols):
    seq, cirurgia_col, _ = build_sequencia(cols)
    base = parse_date_any(row.get(cirurgia_col)) if cirurgia_col else None
    grade = {}
    if base:
        grade["CIRURGIA"] = base
        for rotulo, col, off in seq:
            if rotulo == "CIRURGIA":
                continue
            if off is not None:
                grade[rotulo] = add_months(base, off)
    return grade


# Datas calculadas pelo sistema recebem o sufixo " (auto)" para: (1) aparecerem
# em azul na tabela, (2) poderem ser recalculadas com segurança sem tocar em
# datas confirmadas manualmente ou já coletadas.
AUTO_TAG = "(auto)"
# Espaçamento mínimo entre duas coletas agendadas na recuperação de atraso
# (evita amontoar várias coletas na mesma semana).
MIN_GAP_DAYS = 30
# Ao recuperar um atraso, quão à frente de hoje a nova data pode ficar, no mínimo.
MIN_FUTURE_DAYS = 7


def auto_sched_text(d) -> str:
    """Texto gravado numa célula agendada automaticamente: 'dd/mm/aa (auto)'."""
    return f"{fmt_br(d)} {AUTO_TAG}".strip()


def _is_manual_locked(v) -> bool:
    """
    Célula que NÃO deve ser recalculada pelo sistema:
      • já coletada  → contém '(coletado)'
      • data/valor digitado manualmente (não vazio e sem a marca '(auto)')
    """
    if is_empty_cell(v):
        return False
    if has_collected_tag(v):
        return True
    if is_auto_cell(v):
        return False
    return True   # texto manual (data digitada, 'F', 'NC', etc.)


def _meio_termo(n, targets, today, last_date):
    """
    Nova data 'meio-termo' para uma coleta atrasada, minimizando o atraso:
    ponto médio entre HOJE e o alvo ideal da PRÓXIMA coleta ainda no futuro.
    Se não houver alvo futuro (cirurgia muito antiga), agenda o quanto antes,
    espaçando por metade do intervalo nominal a partir de hoje.
    """
    from datetime import timedelta
    futuros = sorted(
        targets[m] for m in targets
        if m > n and targets.get(m) and targets[m].date() > today
    )
    if futuros:
        nxt = futuros[0]
        delta = (nxt.date() - today)
        return datetime.combine(today + timedelta(days=max(delta.days // 2, MIN_FUTURE_DAYS)),
                                datetime.min.time())
    # sem marco futuro: recuperar rápido, meio intervalo (~3 meses) à frente
    return datetime.combine(today + timedelta(days=90), datetime.min.time())


def compute_bxl_schedule(row, cols, today=None):
    """
    Calcula automaticamente o cronograma de coletas BxL de um paciente a partir
    da data de CIRURGIA, de BxL 2 até BxL 7 (ou o maior BxL existente).

    Regras:
      • células já coletadas ou digitadas manualmente são respeitadas;
      • células vazias ou '(auto)' recebem a data calculada;
      • se o alvo ideal (cirurgia + offset) ainda está no futuro, usa o alvo;
      • se o alvo já passou (coleta atrasada), calcula uma data 'meio-termo'
        para minimizar o atraso;
      • datas '(auto)' que já estão no futuro são mantidas (evita reescrita).

    Retorna dict {coluna: texto_novo} apenas com as células a atualizar.
    """
    from datetime import timedelta
    if today is None:
        today = date.today()

    seq, cirurgia_col, _ = build_sequencia(cols)
    surgery = parse_date_any(row.get(cirurgia_col)) if cirurgia_col else None
    if not surgery:
        return {}

    targets = {}
    for rotulo, col, off in seq:
        if rotulo == "CIRURGIA" or off is None:
            continue
        n = bxl_num(col)
        targets[n] = add_months(surgery, off)

    updates = {}
    last_date = surgery
    for rotulo, col, off in seq:
        if rotulo == "CIRURGIA":
            continue
        n = bxl_num(col)
        ideal = targets.get(n)
        if ideal is None:
            continue
        cur = row.get(col)

        # respeita coleta feita / data manual
        if _is_manual_locked(cur):
            d = parse_date_any(cur)
            if d and d > last_date:
                last_date = d
            continue

        # célula '(auto)' já no futuro → mantém como está
        if is_auto_cell(cur):
            d = parse_date_any(cur)
            if d and d.date() > today:
                last_date = d
                continue

        # precisa (re)agendar: vazia ou '(auto)' atrasada
        if ideal.date() > today:
            newd = ideal
        else:
            newd = _meio_termo(n, targets, today, last_date)

        # garante espaçamento e que fique à frente de hoje
        min_from_prev = last_date + timedelta(days=MIN_GAP_DAYS)
        if newd < min_from_prev:
            newd = min_from_prev
        min_future = datetime.combine(today + timedelta(days=MIN_FUTURE_DAYS), datetime.min.time())
        if newd.date() <= today and ideal.date() <= today and newd < min_future:
            newd = min_future

        novo_txt = auto_sched_text(newd)
        if str(cur).strip() != novo_txt:
            updates[col] = novo_txt
        last_date = newd

    return updates


def autofill_datas_futuras(df, idx_patient, today=None) -> bool:
    """Aplica o cronograma calculado a um paciente. Retorna True se alterou algo."""
    cols = list(df.columns)
    row = df.loc[idx_patient, :]
    updates = compute_bxl_schedule(row, cols, today=today)
    if not updates:
        return False
    for col, txt in updates.items():
        df.at[idx_patient, col] = txt
    return True


def recompute_all_schedules(df, today=None) -> int:
    """
    Recalcula o cronograma de TODOS os pacientes de uma vez.
    Retorna o número de pacientes alterados. Opera in-place no DataFrame.
    """
    changed = 0
    for idx in list(df.index):
        try:
            if autofill_datas_futuras(df, idx, today=today):
                changed += 1
        except Exception:
            continue
    return changed


def coleta_short_label(coleta: str) -> str:
    c = str(coleta or "").strip().lower()
    m = re.search(r"\bbxl\s*(\d+)\b", c)
    if m:
        return f"BxL {int(m.group(1))}"
    if "pos" in c and "rt" in c:
        return "BxL pós-RT"
    if "cirurg" in c:
        return "Cirurgia"
    if re.search(r"\brm\b", c):
        return "RM"
    if re.search(r"\btc\b", c):
        return "TC"
    return str(coleta or "").strip()


# =====================================================================
# Retirada do estudo (exclusão)
# =====================================================================
MOTIVOS_EXCLUSAO = [
    "Faleceu",
    "Desistência",
    "Sem amostra cirúrgica",
    "Não tem BxL 1",
    "Outro",
]


def _limpar_id_cbl_para_exclusao(raw_id: str) -> str:
    s = str(raw_id or "").strip()
    m = re.search(r"\bCBL\s*(\d+)\b", s, flags=re.IGNORECASE)
    if m:
        return f"CBL{int(m.group(1))}"
    return re.sub(r"\s+", "", s).upper()


def _id_ja_tem_falecimento(raw_id: str) -> bool:
    return "+" in str(raw_id or "")


def padronizar_id_exclusao(raw_id: str, motivo: str) -> str:
    """Retirada comum → 'CBLn (exc)'; falecimento → 'CBLn (+) (exc)'."""
    base = _limpar_id_cbl_para_exclusao(raw_id)
    motivo_norm = norm_text(motivo)
    is_falecimento = (
        "faleceu" in motivo_norm
        or "falecimento" in motivo_norm
        or "obito" in motivo_norm
        or "óbito" in motivo_norm
        or _id_ja_tem_falecimento(raw_id)
    )
    return f"{base} (+) (exc)" if is_falecimento else f"{base} (exc)"


COLUNAS_PROTEGIDAS_EXCLUSAO = {
    "TCLE FOTO", "TCLE", "data TCLE", "DATA TCLE",
    "STATUS ESTUDO", "DATA EXCLUSÃO ESTUDO", "MOTIVO EXCLUSÃO",
}
