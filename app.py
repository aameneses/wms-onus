"""
app.py — WMS ONUS EXPRESS v2
Rediseño completo: dark mode #000935 + turquesa #00C9CE
Tipografía Raleway + REM · Cards · Sidebar oscuro · Sistema de diseño coherente
"""
import streamlit as st
from datetime import date, timedelta
import base64, os
import pandas as pd
from database import get_session
import services as svc
import pdf_generator as pdf_gen

# ─── Assets ──────────────────────────────────────────────────
def _b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

ASSETS  = os.path.join(os.path.dirname(__file__), "assets")
LOGO_W  = _b64(os.path.join(ASSETS, "logo_white.png"))
LOGO_C  = _b64(os.path.join(ASSETS, "logo_color.png"))
ICON_T  = _b64(os.path.join(ASSETS, "icon-turquoise.png"))

# ─── Config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="WMS · ONUS EXPRESS",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS — Sistema de diseño Onus WMS ────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=REM:wght@300;400;500;600;700&family=Raleway:wght@700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ══ Reset & base ══════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'REM', sans-serif !important;
}
html { scroll-behavior: smooth; }

/* ══ Canvas principal ══════════════════════════════════ */
.stApp {
    background: #030712 !important;
}
.main .block-container {
    background: #030712 !important;
    padding: 1.5rem 2rem 3rem !important;
    max-width: 1400px !important;
}

/* ══ Sidebar — oscuro marca ════════════════════════════ */
[data-testid="stSidebar"] {
    background: #0a0f1c !important;
    border-right: 1px solid #1d2638 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #9ca3af !important;
    font-family: 'REM', sans-serif !important;
    font-size: 0.875rem !important;
}
[data-testid="stSidebar"] .stRadio [aria-checked="true"] + div p {
    color: #00C9CE !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stRadio > div {
    gap: 2px !important;
}
[data-testid="stSidebar"] .stRadio label {
    padding: 8px 10px !important;
    border-radius: 8px !important;
    transition: background 120ms, color 120ms !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: #161f30 !important;
    color: #e5e7eb !important;
}

/* ══ Sidebar brand block ══════════════════════════════ */
.sidebar-brand {
    padding: 1.25rem 1rem 1rem;
    border-bottom: 1px solid #1d2638;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.sidebar-brand-texts { display: flex; flex-direction: column; line-height: 1.1; }
.sidebar-brand-texts .name {
    font-family: 'Raleway', sans-serif;
    font-weight: 800;
    color: #ffffff;
    font-size: 0.95rem;
    letter-spacing: -0.01em;
}
.sidebar-brand-texts .sub {
    font-size: 0.6rem;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 2px;
}
.sidebar-foot {
    position: absolute;
    bottom: 0;
    left: 0; right: 0;
    padding: 12px 16px;
    border-top: 1px solid #1d2638;
    display: flex;
    align-items: center;
    gap: 10px;
    background: #0a0f1c;
}
.sidebar-avatar {
    width: 32px; height: 32px; border-radius: 50%;
    background: linear-gradient(135deg, #00C9CE, #5b8def);
    display: grid; place-items: center;
    font-weight: 700; font-size: 12px; color: #000935;
    flex-shrink: 0;
}
.sidebar-foot-txt .n { font-weight: 600; font-size: 0.8rem; color: #e5e7eb; }
.sidebar-foot-txt .r { font-size: 0.68rem; color: #6b7280; }

/* ══ Page header card ═════════════════════════════════ */
.page-header {
    background: linear-gradient(135deg, #000935 0%, #001560 100%);
    padding: 1.5rem 2rem;
    border-radius: 14px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    border: 1px solid #1d2638;
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 160px; height: 160px;
    border-radius: 50%;
    background: rgba(0,201,206,0.06);
    pointer-events: none;
}
.page-header-sup {
    color: #00C9CE;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin: 0;
}
.page-header-title {
    color: #ffffff;
    font-size: 1.7rem;
    font-weight: 800;
    font-family: 'Raleway', sans-serif;
    margin: 0;
    line-height: 1.1;
    letter-spacing: -0.02em;
}
.page-header-sub {
    color: #94b4d4;
    font-size: 0.78rem;
    margin: 0;
    margin-top: 2px;
}

/* ══ KPI Cards ════════════════════════════════════════ */
.kpi-card {
    background: #111827;
    border: 1px solid #1d2638;
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent, #00C9CE);
}
.kpi-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--accent, #00C9CE);
    display: inline-block;
    margin-right: 6px;
}
.kpi-label {
    font-size: 0.65rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
}
.kpi-value {
    font-family: 'Raleway', sans-serif;
    font-weight: 800;
    font-size: 2rem;
    color: #ffffff;
    line-height: 1;
    letter-spacing: -0.02em;
}
.kpi-delta {
    margin-top: 0.4rem;
    font-size: 0.72rem;
    color: #6b7280;
    display: flex;
    align-items: center;
    gap: 4px;
}
.kpi-delta.up { color: #10b981; }
.kpi-delta.down { color: #ef4444; }
.kpi-icon-bg {
    position: absolute;
    right: 16px; top: 16px;
    font-size: 1.4rem;
    opacity: 0.15;
}

/* ══ Section titles ════════════════════════════════════ */
.sec-title {
    font-family: 'REM', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    color: #e5e7eb;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1d2638;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sec-title::before {
    content: '';
    display: inline-block;
    width: 3px; height: 14px;
    background: #00C9CE;
    border-radius: 2px;
}
.sec-sub {
    font-size: 0.78rem;
    color: #6b7280;
    margin: -0.4rem 0 0.75rem;
}

/* ══ Card container ════════════════════════════════════ */
.onus-card {
    background: #111827;
    border: 1px solid #1d2638;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}

/* ══ Chip / badge ═════════════════════════════════════ */
.chip {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    border: 1px solid;
}
.chip-accent { background: rgba(0,201,206,0.12); color: #00C9CE; border-color: rgba(0,201,206,0.32); }
.chip-blue   { background: rgba(91,141,239,0.15); color: #5b8def; border-color: rgba(91,141,239,0.3); }
.chip-pink   { background: rgba(236,72,153,0.15); color: #ec4899; border-color: rgba(236,72,153,0.3); }
.chip-amber  { background: rgba(245,158,11,0.15); color: #f59e0b; border-color: rgba(245,158,11,0.3); }
.chip-purple { background: rgba(167,139,250,0.15); color: #a78bfa; border-color: rgba(167,139,250,0.3); }
.chip-green  { background: rgba(16,185,129,0.12); color: #10b981; border-color: rgba(16,185,129,0.3); }

/* ══ Total box ════════════════════════════════════════ */
.total-box {
    background: #000935;
    color: white;
    padding: 1.1rem 1.5rem;
    border-radius: 10px;
    border: 1px solid #1d2638;
    border-left: 4px solid #00C9CE;
    margin: 1rem 0;
}
.total-box .label {
    font-size: 0.65rem; color: #00C9CE;
    letter-spacing: 0.15em; text-transform: uppercase; font-weight: 600;
}
.total-box .amount {
    font-family: 'Raleway', sans-serif;
    font-size: 2rem; font-weight: 800; color: #fff;
    letter-spacing: -0.02em; line-height: 1.1;
}

/* ══ Info pills ═══════════════════════════════════════ */
.precio-info {
    background: rgba(0,201,206,0.08);
    border-left: 3px solid #00C9CE;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: #00C9CE;
    margin: 0.5rem 0;
}
.precio-personalizado {
    background: rgba(245,158,11,0.08);
    border-left: 3px solid #f59e0b;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: #f59e0b;
    margin: 0.5rem 0;
}

/* ══ Dataframe overrides ═══════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #1d2638 !important;
}
[data-testid="stDataFrame"] table {
    background: #111827 !important;
}
[data-testid="stDataFrame"] th {
    background: #0a0f1c !important;
    color: #6b7280 !important;
    font-size: 0.65rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-weight: 600 !important;
    border-bottom: 1px solid #1d2638 !important;
}
[data-testid="stDataFrame"] td {
    color: #e5e7eb !important;
    font-size: 0.82rem !important;
    font-family: 'REM', sans-serif !important;
    border-bottom: 1px solid #161f30 !important;
}
[data-testid="stDataFrame"] tr:hover td {
    background: #161f30 !important;
}

/* ══ Metrics ══════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: #111827 !important;
    border: 1px solid #1d2638 !important;
    border-radius: 10px !important;
    padding: 0.75rem 1rem !important;
}
[data-testid="metric-container"] label {
    color: #6b7280 !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-weight: 600 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-family: 'Raleway', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.4rem !important;
}

/* ══ Buttons ══════════════════════════════════════════ */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'REM', sans-serif !important;
    background: #00C9CE !important;
    color: #000935 !important;
    border: none !important;
    padding: 0.45rem 1.1rem !important;
    font-size: 0.83rem !important;
    transition: all 120ms !important;
}
.stButton > button:hover {
    background: #00b8bd !important;
    box-shadow: 0 0 0 3px rgba(0,201,206,0.2) !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #9ca3af !important;
    border: 1px solid #1d2638 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #111827 !important;
    color: #e5e7eb !important;
}

/* ══ Tabs ═════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1d2638 !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: #6b7280 !important;
    font-family: 'REM', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 0.9rem !important;
    margin-bottom: -1px !important;
    transition: all 120ms !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #e5e7eb !important;
}
.stTabs [aria-selected="true"] {
    color: #00C9CE !important;
    border-bottom-color: #00C9CE !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1rem !important;
}

/* ══ Forms ════════════════════════════════════════════ */
div[data-testid="stForm"] {
    background: #111827 !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
    border: 1px solid #1d2638 !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    background: #161f30 !important;
    border: 1px solid #1d2638 !important;
    color: #e5e7eb !important;
    border-radius: 8px !important;
    font-family: 'REM', sans-serif !important;
    font-size: 0.85rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
    border-color: #00C9CE !important;
    box-shadow: 0 0 0 3px rgba(0,201,206,0.12) !important;
}
.stSelectbox > div > div {
    background: #161f30 !important;
    border: 1px solid #1d2638 !important;
    border-radius: 8px !important;
    color: #e5e7eb !important;
}
.stTextInput label, .stSelectbox label, .stTextArea label,
.stNumberInput label, .stDateInput label {
    color: #9ca3af !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    font-family: 'REM', sans-serif !important;
}

/* ══ Selectbox dropdown ═══════════════════════════════ */
[data-baseweb="popover"] {
    background: #0a0f1c !important;
    border: 1px solid #1d2638 !important;
    border-radius: 8px !important;
}
[data-baseweb="menu"] { background: #0a0f1c !important; }
[data-baseweb="menu"] li {
    color: #e5e7eb !important;
    font-family: 'REM', sans-serif !important;
    font-size: 0.83rem !important;
}
[data-baseweb="menu"] li:hover { background: #161f30 !important; }

/* ══ Radio in sidebar ═════════════════════════════════ */
[data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child {
    background: transparent !important;
    border: none !important;
    width: 0 !important;
    height: 0 !important;
}

/* ══ Expander ═════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1px solid #1d2638 !important;
    border-radius: 10px !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stExpander"] summary {
    color: #e5e7eb !important;
    font-family: 'REM', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 0.75rem 1rem !important;
}
[data-testid="stExpander"] summary:hover { color: #00C9CE !important; }
[data-testid="stExpander"] .streamlit-expanderContent {
    background: #111827 !important;
    padding: 0 1rem 1rem !important;
}

/* ══ Alerts ═══════════════════════════════════════════ */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border: 1px solid !important;
    font-family: 'REM', sans-serif !important;
    font-size: 0.83rem !important;
}
.stSuccess {
    background: rgba(16,185,129,0.08) !important;
    border-color: rgba(16,185,129,0.3) !important;
    color: #10b981 !important;
}
.stWarning {
    background: rgba(245,158,11,0.08) !important;
    border-color: rgba(245,158,11,0.3) !important;
    color: #f59e0b !important;
}
.stError {
    background: rgba(239,68,68,0.08) !important;
    border-color: rgba(239,68,68,0.3) !important;
    color: #ef4444 !important;
}
.stInfo {
    background: rgba(0,201,206,0.08) !important;
    border-color: rgba(0,201,206,0.25) !important;
    color: #00C9CE !important;
}

/* ══ Download button ══════════════════════════════════ */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: #00C9CE !important;
    border: 1px solid rgba(0,201,206,0.4) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(0,201,206,0.08) !important;
    border-color: #00C9CE !important;
}

/* ══ Caption / small text ═════════════════════════════ */
.stCaption, small {
    color: #6b7280 !important;
    font-size: 0.75rem !important;
    font-family: 'REM', sans-serif !important;
}

/* ══ Divider ══════════════════════════════════════════ */
hr {
    border: none !important;
    border-top: 1px solid #1d2638 !important;
    margin: 1rem 0 !important;
}

/* ══ Date input ═══════════════════════════════════════ */
[data-baseweb="calendar"] {
    background: #0a0f1c !important;
    border: 1px solid #1d2638 !important;
}

/* ══ Mono values ══════════════════════════════════════ */
.mono { font-family: 'JetBrains Mono', monospace !important; }
</style>
""", unsafe_allow_html=True)

# ─── Constantes ──────────────────────────────────────────────
TIPOS_LABEL = {
    "almacenaje":           "Almacenaje",
    "picking":              "Picking",
    "empaquetado":          "Empaquetado",
    "carga":                "Carga",
    "descarga":             "Descarga",
    "distribucion-interna": "Dist. Interna",
    "distribucion-externa": "Dist. Externa",
}
TIPO_CHIP = {
    "almacenaje":           "chip-accent",
    "picking":              "chip-blue",
    "empaquetado":          "chip-pink",
    "carga":                "chip-amber",
    "descarga":             "chip-purple",
    "distribucion-interna": "chip-green",
    "distribucion-externa": "chip-green",
}
GRUPOS_OP = {
    "📦 Almacenaje":             ["almacenaje"],
    "📋 Preparación de pedidos": ["picking", "empaquetado"],
    "🚛 Cargas / Descargas":     ["carga", "descarga"],
    "🚚 Distribución":           ["distribucion-interna", "distribucion-externa"],
}
MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
COND_PAGO = ["30 días neto","15 días neto","60 días neto","Contado","Personalizado"]

# ─── DB helpers ──────────────────────────────────────────────
def get_db():
    try:
        if "db" in st.session_state:
            try: st.session_state.db.close()
            except: pass
        st.session_state.db = get_session()
        return st.session_state.db
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.stop()

def refresh_db():
    global db
    try: st.session_state.db.close()
    except: pass
    st.session_state.db = get_session()
    db = st.session_state.db

db = get_db()

def cli_opts():
    return {f"{c.empresa or '—'}  ·  {c.nombre}": c.id
            for c in svc.get_all_clientes(db)}

def tar_opts():
    return {t.nombre: t.id for t in svc.get_all_tarifas(db)}

# ─── Componentes UI ──────────────────────────────────────────
def page_header(titulo: str, subtitulo: str = "", sup: str = "ONUS EXPRESS · WMS"):
    logo_tag = (f'<img src="data:image/png;base64,{LOGO_W}" style="height:40px;">'
                if LOGO_W else
                '<div style="width:40px;height:40px;border-radius:8px;'
                'background:#00C9CE;display:grid;place-items:center;'
                'font-family:Raleway,sans-serif;font-weight:800;font-size:1rem;color:#000935;">O</div>')
    st.markdown(f"""
    <div class="page-header">
        {logo_tag}
        <div>
            <p class="page-header-sup">{sup}</p>
            <p class="page-header-title">{titulo}</p>
            {'<p class="page-header-sub">' + subtitulo + '</p>' if subtitulo else ''}
        </div>
    </div>""", unsafe_allow_html=True)

def sec(titulo, subtitulo=""):
    st.markdown(f'<div class="sec-title">{titulo}</div>', unsafe_allow_html=True)
    if subtitulo:
        st.markdown(f'<div class="sec-sub">{subtitulo}</div>', unsafe_allow_html=True)

def kpi(label, value, icon="", delta="", delta_up=True, accent="#00C9CE"):
    delta_cls = "up" if delta_up else "down"
    arrow = "↑" if delta_up else "↓"
    delta_html = f'<div class="kpi-delta {delta_cls}">{arrow} {delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card" style="--accent:{accent}">
        <div class="kpi-icon-bg">{icon}</div>
        <div class="kpi-label"><span class="kpi-dot" style="background:{accent}"></span>{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>""", unsafe_allow_html=True)

def chip(texto, clase="chip-accent"):
    return f'<span class="chip {clase}">{texto}</span>'

def tipo_chip_html(tipo):
    label = TIPOS_LABEL.get(tipo, tipo)
    clase = TIPO_CHIP.get(tipo, "chip-accent")
    return chip(label, clase)

# ─── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    icon_src = (f'<img src="data:image/png;base64,{ICON_T}" style="width:32px;height:32px;object-fit:contain;">'
                if ICON_T else
                '<div style="width:32px;height:32px;border-radius:8px;background:#00C9CE;'
                'display:grid;place-items:center;font-family:Raleway;font-weight:800;color:#000935;">O</div>')
    st.markdown(f"""
    <div class="sidebar-brand">
        {icon_src}
        <div class="sidebar-brand-texts">
            <span class="name">Onus WMS</span>
            <span class="sub">v2.4 · Express</span>
        </div>
    </div>""", unsafe_allow_html=True)

    pagina = st.radio("", [
        "🏠 Dashboard", "👥 Clientes", "💰 Tarifas",
        "📋 Operaciones", "📦 Stock", "📊 Reportes", "🧾 Facturación"
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown(
        f'<small style="color:#4b5563;padding:0 0.5rem;">'
        f'📅 {date.today().strftime("%d · %m · %Y")}</small>',
        unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-foot">
        <div class="sidebar-avatar">AM</div>
        <div class="sidebar-foot-txt">
            <div class="n">Alejandro M.</div>
            <div class="r">Administrador</div>
        </div>
    </div>""", unsafe_allow_html=True)

pag = pagina.split(" ", 1)[1]

# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
if pag == "Dashboard":
    page_header("Dashboard", "Visión global del almacén · " + date.today().strftime("%d de %B de %Y"))
    refresh_db()
    try:
        kpis = svc.get_kpis_dashboard(db)
    except Exception as e:
        st.error(f"Error: {e}"); st.stop()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi("Clientes",          str(kpis["total_clientes"]),      "👥", "", accent="#00C9CE")
    with c2: kpi("Pallets activos",   str(kpis["pallets_activos"]),     "📦", "", accent="#5b8def")
    with c3: kpi("Operaciones · mes", str(kpis["ops_mes"]),             "⚡", "", accent="#f59e0b")
    with c4: kpi("Facturado · mes",   f"{kpis['facturacion_mes']:,.0f}€","📈","vs. mes anterior", accent="#10b981")
    with c5: kpi("Total facturado",   f"{kpis['total_facturado']:,.0f}€","💰","histórico", accent="#a78bfa")

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)
    cl, cr = st.columns([3, 2])

    with cl:
        sec("Últimas operaciones")
        movs = svc.get_all_movimientos(db)[:12]
        if movs:
            rows = []
            for m in movs:
                c_ = svc.get_cliente_by_id(db, m.cliente_id)
                rows.append({
                    "Fecha":    m.fecha.strftime("%d/%m/%Y"),
                    "Empresa":  c_.empresa if c_ else "—",
                    "Tipo":     TIPOS_LABEL.get(m.tipo, m.tipo),
                    "Cant.":    float(m.cantidad),
                    "Coste €":  f"{float(m.coste or 0):,.2f}",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("Sin operaciones registradas.")

    with cr:
        sec("Stock activo")
        stock = svc.get_stock_activo(db)[:10]
        if stock:
            rows = []
            for s in stock:
                c_ = svc.get_cliente_by_id(db, s.cliente_id)
                dias = (date.today() - s.fecha_entrada).days
                rows.append({
                    "Empresa":   c_.empresa if c_ else "—",
                    "Pallet":    s.pallet,
                    "Días":      dias,
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No hay pallets en almacén.")

# ══════════════════════════════════════════════════════════════
# CLIENTES
# ══════════════════════════════════════════════════════════════
elif pag == "Clientes":
    page_header("Clientes", "Alta, edición y condiciones comerciales")
    refresh_db()

    tab_lista, tab_nuevo, tab_editar, tab_tarifa_esp = st.tabs([
        "Listado", "Nuevo cliente", "Editar · Eliminar", "Tarifa especial"
    ])

    with tab_lista:
        sec("Clientes registrados", "Todos los clientes activos en el sistema")
        clientes = svc.get_all_clientes(db)
        if clientes:
            data = [{
                "ID":       c.id,
                "Empresa":  c.empresa or "—",
                "Contacto": c.nombre,
                "Email":    c.email or "—",
                "Teléfono": c.telefono or "—",
                "Tarifa":   c.tarifa.nombre if c.tarifa else "⚠️ Sin tarifa",
                "Pago":     c.condiciones_pago or "—",
            } for c in clientes]
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
            st.caption(f"{len(clientes)} clientes registrados")
        else:
            st.info("No hay clientes. Usa la pestaña 'Nuevo cliente' para añadir el primero.")

    with tab_nuevo:
        sec("Nuevo cliente")
        tm = tar_opts()
        with st.form("form_nuevo_cli", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                empresa  = st.text_input("Empresa / Razón social *", placeholder="Distribuciones García S.L.")
                nombre   = st.text_input("Persona de contacto *",    placeholder="Juan García")
                email    = st.text_input("Email",                    placeholder="juan@empresa.com")
            with col2:
                telefono = st.text_input("Teléfono",                 placeholder="612 345 678")
                cond     = st.selectbox("Condiciones de pago",       COND_PAGO)
                tar_sel  = st.selectbox("Tarifa asignada",           ["Sin tarifa"] + list(tm.keys()))
            if st.form_submit_button("Guardar cliente", type="primary", use_container_width=True):
                if not empresa.strip() or not nombre.strip():
                    st.error("Empresa y persona de contacto son obligatorios.")
                else:
                    tid = tm.get(tar_sel) if tar_sel != "Sin tarifa" else None
                    svc.create_cliente(db, {
                        "nombre": nombre.strip(), "empresa": empresa.strip(),
                        "email": email.strip() or None, "telefono": telefono.strip() or None,
                        "condiciones_pago": cond, "tarifa_id": tid,
                    })
                    st.success(f"Cliente '{empresa}' creado correctamente.")
                    st.rerun()

    with tab_editar:
        sec("Editar o eliminar cliente")
        clientes = svc.get_all_clientes(db)
        if not clientes:
            st.info("No hay clientes.")
        else:
            cm = {f"{c.empresa or '—'} · {c.nombre}": c.id for c in clientes}
            sel = st.selectbox("Selecciona el cliente", list(cm.keys()))
            c   = svc.get_cliente_by_id(db, cm[sel])
            tm  = tar_opts()
            if c:
                st.markdown("---")
                with st.form("form_edit_cli"):
                    col1, col2 = st.columns(2)
                    with col1:
                        emp_e = st.text_input("Empresa *",     value=c.empresa or "")
                        nom_e = st.text_input("Contacto *",    value=c.nombre)
                        eml_e = st.text_input("Email",         value=c.email or "")
                    with col2:
                        tel_e = st.text_input("Teléfono",      value=c.telefono or "")
                        ci    = COND_PAGO.index(c.condiciones_pago) if c.condiciones_pago in COND_PAGO else 0
                        cnd_e = st.selectbox("Condiciones pago", COND_PAGO, index=ci)
                        tns   = ["Sin tarifa"] + list(tm.keys())
                        ta    = c.tarifa.nombre if c.tarifa else "Sin tarifa"
                        ti    = tns.index(ta) if ta in tns else 0
                        tar_e = st.selectbox("Tarifa", tns, index=ti)

                    cg, cd = st.columns([3, 1])
                    with cg: guardar  = st.form_submit_button("Actualizar", type="primary", use_container_width=True)
                    with cd: eliminar = st.form_submit_button("Eliminar",   use_container_width=True)

                    if guardar:
                        tid = tm.get(tar_e) if tar_e != "Sin tarifa" else None
                        svc.update_cliente(db, c.id, {
                            "nombre": nom_e, "empresa": emp_e or None,
                            "email": eml_e or None, "telefono": tel_e or None,
                            "condiciones_pago": cnd_e, "tarifa_id": tid,
                        })
                        st.success("Cliente actualizado."); st.rerun()
                    if eliminar:
                        svc.delete_cliente(db, c.id)
                        st.warning("Cliente eliminado."); st.rerun()

    with tab_tarifa_esp:
        sec("Tarifa especial por cliente",
            "Precios negociados que sobrescriben la tarifa general")
        clientes = svc.get_all_clientes(db)
        if not clientes:
            st.info("No hay clientes.")
        else:
            cm2  = {f"{c.empresa or '—'} · {c.nombre}": c.id for c in clientes}
            sel2 = st.selectbox("Cliente", list(cm2.keys()), key="cli_tar_esp")
            cid2 = cm2[sel2]
            c2   = svc.get_cliente_by_id(db, cid2)

            if c2 and c2.tarifa:
                st.info(f"Tarifa general activa: **{c2.tarifa.nombre}** — los precios especiales tienen prioridad.")

            tcs = svc.get_tarifas_cliente(db, cid2)
            if tcs:
                sec("Precios especiales activos")
                rows_tc = [{
                    "ID":       t.id,
                    "Servicio": TIPOS_LABEL.get(t.tipo_servicio, t.tipo_servicio),
                    "Cálculo":  svc.CALCULO_LABEL.get(t.tipo_calculo, t.tipo_calculo),
                    "Precio €": float(t.precio),
                    "Nota":     t.descripcion or "—",
                } for t in tcs]
                st.dataframe(pd.DataFrame(rows_tc), use_container_width=True, hide_index=True)

                col_del1, col_del2 = st.columns([2, 1])
                with col_del1:
                    id_del_tc = st.number_input("ID a eliminar", min_value=1, step=1)
                with col_del2:
                    st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
                    if st.button("Eliminar precio especial"):
                        svc.delete_tarifa_cliente(db, int(id_del_tc))
                        st.success("Eliminado."); st.rerun()
            else:
                st.info("Sin precios especiales — se aplica la tarifa general.")

            st.markdown("---")
            sec("Añadir precio especial")
            with st.form("form_tar_esp", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    tipo_srv = st.selectbox("Tipo de servicio *",
                                            [TIPOS_LABEL[t] for t in svc.TIPOS_SERVICIO])
                    tipo_srv_key = svc.TIPOS_SERVICIO[
                        [TIPOS_LABEL[t] for t in svc.TIPOS_SERVICIO].index(tipo_srv)]
                with col2:
                    tipo_calc = st.selectbox("Tipo de cálculo *",
                                             list(svc.CALCULO_LABEL.values()))
                    tipo_calc_key = svc.CALCULO_OPTS[
                        list(svc.CALCULO_LABEL.values()).index(tipo_calc)]
                with col3:
                    precio_esp = st.number_input("Precio €", min_value=0.0, step=0.05, format="%.2f")
                desc_esp = st.text_input("Nota interna", placeholder="Ej. Acuerdo contrato 2025")
                if st.form_submit_button("Guardar precio especial", type="primary", use_container_width=True):
                    svc.upsert_tarifa_cliente(db, cid2, tipo_srv_key, tipo_calc_key, precio_esp, desc_esp)
                    st.success(f"Precio especial guardado para {tipo_srv}."); st.rerun()

# ══════════════════════════════════════════════════════════════
# TARIFAS
# ══════════════════════════════════════════════════════════════
elif pag == "Tarifas":
    page_header("Tarifas", "Configuración de precios por tipo de servicio")
    refresh_db()

    tab_lista, tab_nueva, tab_detalle = st.tabs([
        "Tarifas", "Nueva tarifa", "Precios por servicio"
    ])

    with tab_lista:
        sec("Tarifas disponibles")
        tarifas = svc.get_all_tarifas(db)
        if tarifas:
            for t in tarifas:
                with st.expander(f"📋  {t.nombre}"):
                    detalles = svc.get_detalles_tarifa(db, t.id)
                    if detalles:
                        rows = [{
                            "Servicio":  TIPOS_LABEL.get(d.tipo_servicio, d.tipo_servicio),
                            "Cálculo":   svc.CALCULO_LABEL.get(d.tipo_calculo, d.tipo_calculo),
                            "Precio €":  float(d.precio),
                            "Descripción": d.descripcion or "—",
                        } for d in detalles]
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    else:
                        st.caption("Sin precios detallados — usando precios base.")
                        st.write(
                            f"Almacenaje: **{float(t.precio_pallet_dia):.2f} €/día**  ·  "
                            f"Picking: **{float(t.precio_picking):.2f} €/ud**  ·  "
                            f"Carga: **{float(t.precio_carga):.2f} €**  ·  "
                            f"Descarga: **{float(t.precio_descarga):.2f} €**"
                        )
                    if st.button("Eliminar tarifa", key=f"del_tar_{t.id}"):
                        svc.delete_tarifa(db, t.id)
                        st.warning("Tarifa eliminada."); st.rerun()
        else:
            st.info("No hay tarifas. Crea la primera en la pestaña 'Nueva tarifa'.")

    with tab_nueva:
        sec("Crear tarifa")
        with st.form("form_nueva_tar", clear_on_submit=True):
            nombre_t = st.text_input("Nombre de la tarifa *",
                                     placeholder="Ej. Tarifa Estándar 2025")
            col1, col2, col3, col4 = st.columns(4)
            with col1: pp  = st.number_input("Almacenaje €/pallet/día", min_value=0.0, step=0.05, value=0.75, format="%.2f")
            with col2: pk  = st.number_input("Picking / Empaq. €/ud",   min_value=0.0, step=0.05, value=1.50, format="%.2f")
            with col3: pc  = st.number_input("Carga €/operación",        min_value=0.0, step=1.0,  value=35.0, format="%.2f")
            with col4: pd_ = st.number_input("Descarga €/operación",     min_value=0.0, step=1.0,  value=35.0, format="%.2f")
            if st.form_submit_button("Crear tarifa", type="primary", use_container_width=True):
                if not nombre_t.strip():
                    st.error("El nombre es obligatorio.")
                else:
                    t = svc.create_tarifa(db, {
                        "nombre": nombre_t.strip(), "precio_pallet_dia": pp,
                        "precio_picking": pk, "precio_carga": pc, "precio_descarga": pd_,
                    })
                    for tipo, calc, precio, desc in [
                        ("almacenaje",           "por_dia",    pp,  "Almacenaje por pallet/día"),
                        ("picking",              "por_unidad", pk,  "Picking por unidad"),
                        ("empaquetado",          "por_unidad", pk,  "Empaquetado por unidad"),
                        ("carga",                "fijo",       pc,  "Carga por operación"),
                        ("descarga",             "fijo",       pd_, "Descarga por operación"),
                        ("distribucion-interna", "por_unidad", pk,  "Distribución interna"),
                        ("distribucion-externa", "por_unidad", pk,  "Distribución externa"),
                    ]:
                        svc.upsert_detalle_tarifa(db, t.id, tipo, calc, precio, desc)
                    st.success(f"Tarifa '{nombre_t}' creada."); st.rerun()

    with tab_detalle:
        sec("Editar precios por servicio")
        tarifas = svc.get_all_tarifas(db)
        if not tarifas:
            st.info("Primero crea una tarifa.")
        else:
            tm2    = {t.nombre: t.id for t in tarifas}
            sel_t  = st.selectbox("Tarifa a editar", list(tm2.keys()))
            tar_id = tm2[sel_t]
            detalles = svc.get_detalles_tarifa(db, tar_id)
            det_map  = {d.tipo_servicio: d for d in detalles}

            with st.form("form_detalle_tar"):
                filas = []
                for tipo in svc.TIPOS_SERVICIO:
                    d = det_map.get(tipo)
                    col1, col2, col3 = st.columns([3, 2, 2])
                    with col1:
                        st.markdown(f"**{TIPOS_LABEL[tipo]}**")
                        desc_v = st.text_input("Descripción", value=d.descripcion or "" if d else "",
                                               key=f"desc_{tipo}", label_visibility="collapsed",
                                               placeholder="Descripción interna...")
                    with col2:
                        calcs  = list(svc.CALCULO_LABEL.values())
                        c_idx  = calcs.index(svc.CALCULO_LABEL.get(d.tipo_calculo, "por_unidad")) if d else 0
                        calc_v = st.selectbox("Cálculo", calcs, index=c_idx,
                                              key=f"calc_{tipo}", label_visibility="collapsed")
                    with col3:
                        prec_v = st.number_input("Precio €", min_value=0.0, step=0.05,
                                                 value=float(d.precio) if d else 0.0,
                                                 format="%.2f", key=f"prec_{tipo}",
                                                 label_visibility="collapsed")
                    filas.append((tipo, calc_v, prec_v, desc_v))

                if st.form_submit_button("Guardar precios", type="primary", use_container_width=True):
                    for tipo, calc_lbl, precio, desc in filas:
                        calc_key = svc.CALCULO_OPTS[list(svc.CALCULO_LABEL.values()).index(calc_lbl)]
                        svc.upsert_detalle_tarifa(db, tar_id, tipo, calc_key, precio, desc)
                    st.success(f"Precios de '{sel_t}' actualizados."); st.rerun()

# ══════════════════════════════════════════════════════════════
# OPERACIONES
# ══════════════════════════════════════════════════════════════
elif pag == "Operaciones":
    page_header("Operaciones", "Registro de actividad del almacén")
    refresh_db()

    tab_nuevo, tab_hist = st.tabs(["Nueva operación", "Historial"])

    with tab_nuevo:
        sec("Registrar operación")
        cm = cli_opts()
        if not cm:
            st.warning("Primero debes crear clientes.")
        else:
            grupo = st.selectbox("Grupo de operación", list(GRUPOS_OP.keys()))
            with st.form("form_op", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    cli_sel  = st.selectbox("Cliente *", list(cm.keys()))
                    tipos_g  = GRUPOS_OP[grupo]
                    tipo_lbs = [TIPOS_LABEL[t] for t in tipos_g]
                    tipo_lb  = st.selectbox("Tipo de servicio *", tipo_lbs)
                    tipo_key = tipos_g[tipo_lbs.index(tipo_lb)]
                with col2:
                    cantidad = st.number_input("Cantidad *", min_value=0.01, step=1.0, value=1.0, format="%.2f")
                    fecha_op = st.date_input("Fecha *", value=date.today())
                with col3:
                    obs = st.text_area("Observaciones",
                                       placeholder="Nº pedido, albarán, referencia...",
                                       height=110)

                cid_prev = cm.get(cli_sel)
                if cid_prev:
                    info = svc.resolver_precio(db, cid_prev, tipo_key)
                    coste_est = svc.calcular_coste(info["precio"], info["tipo_calculo"], float(cantidad))
                    fuente_txt = {
                        "personalizada":  "⭐ Precio especial negociado",
                        "tarifa_general": "📋 Tarifa general asignada",
                        "legacy":         "📋 Tarifa base",
                        "sin_tarifa":     "⚠️ Sin tarifa — coste 0 €",
                    }.get(info["fuente"], "")
                    css_cls = "precio-personalizado" if info["fuente"] == "personalizada" else "precio-info"
                    st.markdown(f"""
                    <div class="{css_cls}">
                        Coste estimado: <strong>{coste_est:.2f} €</strong> &nbsp;·&nbsp;
                        {svc.CALCULO_LABEL.get(info["tipo_calculo"],"")} a {info["precio"]:.2f} €
                        &nbsp;·&nbsp; {fuente_txt}
                    </div>""", unsafe_allow_html=True)

                if st.form_submit_button("Registrar operación", type="primary", use_container_width=True):
                    svc.create_movimiento(db, {
                        "cliente_id": cm[cli_sel], "tipo": tipo_key,
                        "cantidad": cantidad, "fecha": fecha_op,
                        "observaciones": obs.strip() or None,
                    })
                    st.success(f"Operación '{tipo_lb}' registrada correctamente.")
                    st.rerun()

    with tab_hist:
        sec("Historial de operaciones", "Filtra por cliente, tipo y período")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            cm2   = {"Todos los clientes": None} | cli_opts()
            f_cli = st.selectbox("Cliente", list(cm2.keys()))
        with col2:
            f_grp = st.selectbox("Grupo", ["Todos"] + list(GRUPOS_OP.keys()))
        with col3:
            f_desde = st.date_input("Desde", value=date.today() - timedelta(days=30))
        with col4:
            f_hasta = st.date_input("Hasta", value=date.today())

        tipos_f = GRUPOS_OP.get(f_grp) if f_grp != "Todos" else None
        movs    = svc.get_all_movimientos(db, cliente_id=cm2.get(f_cli),
                                          fecha_desde=f_desde, fecha_hasta=f_hasta)
        if tipos_f:
            movs = [m for m in movs if m.tipo in tipos_f]

        if movs:
            rows = []
            for m in movs:
                c_ = svc.get_cliente_by_id(db, m.cliente_id)
                rows.append({
                    "ID":       m.id,
                    "Fecha":    m.fecha.strftime("%d/%m/%Y"),
                    "Empresa":  c_.empresa if c_ else "—",
                    "Tipo":     TIPOS_LABEL.get(m.tipo, m.tipo),
                    "Cantidad": float(m.cantidad),
                    "Coste €":  float(m.coste or 0),
                    "Obs.":     (m.observaciones or "")[:55],
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Operaciones",    len(movs))
            mc2.metric("Unidades",       int(sum(float(m.cantidad) for m in movs)))
            mc3.metric("Coste total",    f"{sum(float(m.coste or 0) for m in movs):,.2f} €")

            st.markdown("---")
            ci, cb = st.columns([2, 1])
            with ci: id_del = st.number_input("ID a eliminar", min_value=1, step=1)
            with cb:
                st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
                if st.button("Eliminar operación"):
                    if svc.delete_movimiento(db, int(id_del)):
                        st.success("Eliminada."); st.rerun()
                    else:
                        st.error("ID no encontrado.")
        else:
            st.info("No hay operaciones con los filtros seleccionados.")

# ══════════════════════════════════════════════════════════════
# STOCK
# ══════════════════════════════════════════════════════════════
elif pag == "Stock":
    page_header("Stock", "Pallets en almacén · Entradas y salidas")
    refresh_db()

    tab_act, tab_ent, tab_sal = st.tabs(["Stock activo", "Entrada de pallet", "Dar salida"])

    with tab_act:
        sec("Pallets activos en almacén")
        cm_s = {"Todos los clientes": None} | cli_opts()
        f_s  = st.selectbox("Filtrar por cliente", list(cm_s.keys()))
        stck = svc.get_stock_activo(db, cliente_id=cm_s.get(f_s))
        if stck:
            rows = []
            for s in stck:
                c_   = svc.get_cliente_by_id(db, s.cliente_id)
                dias = (date.today() - s.fecha_entrada).days
                info = svc.resolver_precio(db, s.cliente_id, "almacenaje")
                rows.append({
                    "ID":          s.id,
                    "Empresa":     c_.empresa if c_ else "—",
                    "Pallet":      s.pallet,
                    "Referencia":  s.referencia or "—",
                    "Cantidad":    s.cantidad,
                    "F. Entrada":  s.fecha_entrada.strftime("%d/%m/%Y"),
                    "Días":        dias,
                    "Coste acum.": f"{round(dias * info['precio'] * s.cantidad, 2):,.2f} €",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            sc1, sc2 = st.columns(2)
            sc1.metric("Pallets activos", len(stck))
            total_acum = sum(
                (date.today() - s.fecha_entrada).days
                * svc.resolver_precio(db, s.cliente_id, "almacenaje")["precio"]
                * s.cantidad
                for s in stck
            )
            sc2.metric("Coste acumulado", f"{total_acum:,.2f} €")
        else:
            st.info("No hay pallets en almacén.")

    with tab_ent:
        sec("Registrar entrada de pallet")
        cm_e = cli_opts()
        if not cm_e:
            st.warning("Crea clientes primero.")
        else:
            with st.form("form_ent", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    cli_e = st.selectbox("Cliente *",    list(cm_e.keys()))
                    pal_e = st.text_input("Código pallet *", placeholder="PAL-001")
                    ref_e = st.text_input("Referencia",      placeholder="REF-X100")
                with col2:
                    qty_e = st.number_input("Número de pallets", min_value=1, step=1, value=1)
                    fec_e = st.date_input("Fecha de entrada *", value=date.today())
                    obs_e = st.text_input("Observaciones", placeholder="Nº albarán, proveedor...")

                if st.form_submit_button("Registrar entrada", type="primary", use_container_width=True):
                    if not pal_e.strip():
                        st.error("El código de pallet es obligatorio.")
                    else:
                        svc.create_stock(db, {
                            "cliente_id": cm_e[cli_e], "pallet": pal_e.strip(),
                            "referencia": ref_e.strip() or None, "cantidad": qty_e,
                            "fecha_entrada": fec_e,
                            "observaciones": obs_e.strip() or None, "activo": True,
                        })
                        st.success(f"Pallet '{pal_e}' registrado."); st.rerun()

    with tab_sal:
        sec("Dar salida a un pallet")
        sa = svc.get_stock_activo(db)
        if not sa:
            st.info("No hay pallets activos.")
        else:
            pm = {}
            for s in sa:
                c_ = svc.get_cliente_by_id(db, s.cliente_id)
                pm[f"#{s.id} · {s.pallet} · {c_.empresa if c_ else '—'} · entrada {s.fecha_entrada.strftime('%d/%m/%Y')}"] = s.id
            sel_p   = st.selectbox("Pallet a retirar", list(pm.keys()))
            fec_sal = st.date_input("Fecha de salida", value=date.today())
            if st.button("Confirmar salida de almacén", type="primary"):
                svc.dar_salida_pallet(db, pm[sel_p], fec_sal)
                st.success("Pallet dado de baja."); st.rerun()

# ══════════════════════════════════════════════════════════════
# REPORTES
# ══════════════════════════════════════════════════════════════
elif pag == "Reportes":
    page_header("Reportes", "Análisis de actividad y facturación")
    refresh_db()

    hoy = date.today()
    col_m, col_a = st.columns(2)
    with col_m: mes  = st.selectbox("Mes",  range(1, 13), index=hoy.month-1,
                                    format_func=lambda x: MESES[x-1])
    with col_a: anio = st.selectbox("Año",  range(2023, hoy.year+2), index=hoy.year-2023)

    tab_alm, tab_prep, tab_cd, tab_dist, tab_men = st.tabs([
        "Almacenaje", "Preparación", "Cargas · Descargas", "Distribución", "Resumen mensual"
    ])

    with tab_alm:
        sec("Informe de almacenaje", f"{MESES[mes-1]} {anio}")
        rows = svc.reporte_almacenaje(db, mes, anio)
        if rows:
            df = pd.DataFrame([{
                "Cliente":   r["cliente"],   "Empresa":   r["empresa"],
                "Pallet":    r["pallet"],    "Referencia":r["referencia"],
                "Entrada":   r["fecha_entrada"].strftime("%d/%m/%Y"),
                "Salida":    r["fecha_salida"].strftime("%d/%m/%Y") if r.get("fecha_salida") else "En almacén",
                "Días":      r["dias"],      "€/día":     r["precio_dia"],
                "Total €":   r["coste"],
            } for r in rows])
            st.dataframe(df, use_container_width=True, hide_index=True)
            rc1, rc2 = st.columns(2)
            rc1.metric("Pallets facturados", len(rows))
            rc2.metric("Total almacenaje",   f"{sum(r['coste'] for r in rows):,.2f} €")
            pdf_b = pdf_gen.generar_pdf_almacenaje(rows, mes, anio)
            st.download_button("⬇  PDF Almacenaje", data=pdf_b,
                               file_name=f"almacenaje_{anio}_{mes:02d}.pdf",
                               mime="application/pdf", type="primary")
        else:
            st.info("Sin datos de almacenaje en este período.")

    with tab_prep:
        sec("Preparación de pedidos", f"Picking y empaquetado · {MESES[mes-1]} {anio}")
        rows = []
        for t in ["picking", "empaquetado"]:
            rows += svc.reporte_operaciones(db, mes, anio, t)
        rows.sort(key=lambda x: x["fecha"], reverse=True)
        if rows:
            df = pd.DataFrame([{
                "ID": r["id"], "Fecha": r["fecha"].strftime("%d/%m/%Y"),
                "Cliente": r["cliente"], "Tipo": TIPOS_LABEL.get(r["tipo"], r["tipo"]),
                "Cantidad": r["cantidad"], "Coste €": r["coste"],
                "Obs.": r["observaciones"][:50],
            } for r in rows])
            st.dataframe(df, use_container_width=True, hide_index=True)
            pc1, pc2, pc3 = st.columns(3)
            pc1.metric("Operaciones", len(rows))
            pc2.metric("Unidades",    int(sum(r["cantidad"] for r in rows)))
            pc3.metric("Coste total", f"{sum(r['coste'] for r in rows):,.2f} €")
            pdf_b = pdf_gen.generar_pdf_operaciones(rows, "picking", mes, anio)
            st.download_button("⬇  PDF Preparación", data=pdf_b,
                               file_name=f"preparacion_{anio}_{mes:02d}.pdf",
                               mime="application/pdf", type="primary")
        else:
            st.info("Sin preparaciones en este período.")

    with tab_cd:
        sec("Cargas y descargas", f"{MESES[mes-1]} {anio}")
        rows = []
        for t in ["carga", "descarga"]:
            rows += svc.reporte_operaciones(db, mes, anio, t)
        rows.sort(key=lambda x: x["fecha"], reverse=True)
        if rows:
            df = pd.DataFrame([{
                "ID": r["id"], "Fecha": r["fecha"].strftime("%d/%m/%Y"),
                "Cliente": r["cliente"], "Tipo": TIPOS_LABEL.get(r["tipo"], r["tipo"]),
                "Cantidad": r["cantidad"], "Coste €": r["coste"],
                "Obs.": r["observaciones"][:50],
            } for r in rows])
            st.dataframe(df, use_container_width=True, hide_index=True)
            cd1, cd2, cd3, cd4 = st.columns(4)
            cd1.metric("Cargas",     sum(1 for r in rows if r["tipo"] == "carga"))
            cd2.metric("Descargas",  sum(1 for r in rows if r["tipo"] == "descarga"))
            cd3.metric("Unidades",   int(sum(r["cantidad"] for r in rows)))
            cd4.metric("Coste total",f"{sum(r['coste'] for r in rows):,.2f} €")
            pdf_b = pdf_gen.generar_pdf_operaciones(rows, "carga", mes, anio)
            st.download_button("⬇  PDF Cargas/Descargas", data=pdf_b,
                               file_name=f"cargas_{anio}_{mes:02d}.pdf",
                               mime="application/pdf", type="primary")
        else:
            st.info("Sin cargas/descargas en este período.")

    with tab_dist:
        sec("Distribución", f"{MESES[mes-1]} {anio}")
        rows = []
        for t in ["distribucion-interna", "distribucion-externa"]:
            rows += svc.reporte_operaciones(db, mes, anio, t)
        if rows:
            df = pd.DataFrame([{
                "ID": r["id"], "Fecha": r["fecha"].strftime("%d/%m/%Y"),
                "Cliente": r["cliente"], "Tipo": TIPOS_LABEL.get(r["tipo"], r["tipo"]),
                "Cantidad": r["cantidad"], "Coste €": r["coste"],
                "Obs.": r["observaciones"][:50],
            } for r in rows])
            st.dataframe(df, use_container_width=True, hide_index=True)
            dd1, dd2, dd3 = st.columns(3)
            dd1.metric("Interna", sum(1 for r in rows if r["tipo"] == "distribucion-interna"))
            dd2.metric("Externa", sum(1 for r in rows if r["tipo"] == "distribucion-externa"))
            dd3.metric("Coste total", f"{sum(r['coste'] for r in rows):,.2f} €")
        else:
            st.info("Sin distribuciones en este período.")

    with tab_men:
        sec("Resumen mensual global", f"Todos los clientes · {MESES[mes-1]} {anio}")
        res = svc.reporte_mensual_cliente(db, mes, anio)
        if res:
            df = pd.DataFrame([{
                "Empresa":        r["empresa"],
                "Tarifa":         r["tarifa"],
                "Pallets":        r["pallets_almacenados"],
                "Almacenaje €":   r["total_almacenaje"],
                "Preparación €":  r["picking_coste"],
                "Cargas €":       r["cargas_coste"],
                "Descargas €":    r["descargas_coste"],
                "Distribución €": r["distribucion_coste"],
                "TOTAL €":        r["total"],
            } for r in res])
            st.dataframe(df, use_container_width=True, hide_index=True)
            grand = sum(r["total"] for r in res)
            st.markdown(f"""
            <div class="total-box">
                <div class="label">FACTURACIÓN TOTAL DEL MES</div>
                <div class="amount">{grand:,.2f} €</div>
            </div>""", unsafe_allow_html=True)
            pdf_b = pdf_gen.generar_pdf_resumen_mensual(res, mes, anio)
            st.download_button("⬇  PDF Resumen Mensual", data=pdf_b,
                               file_name=f"resumen_{anio}_{mes:02d}.pdf",
                               mime="application/pdf", type="primary")
        else:
            st.info("Sin actividad en este período.")

# ══════════════════════════════════════════════════════════════
# FACTURACIÓN
# ══════════════════════════════════════════════════════════════
elif pag == "Facturación":
    page_header("Facturación", "Resumen y PDF por cliente")
    refresh_db()

    hoy = date.today()
    col_m, col_a, col_c = st.columns(3)
    with col_m: mes_f  = st.selectbox("Mes", range(1, 13), index=hoy.month-1,
                                       format_func=lambda x: MESES[x-1], key="mes_f")
    with col_a: anio_f = st.selectbox("Año", range(2023, hoy.year+2),
                                       index=hoy.year-2023, key="anio_f")
    with col_c:
        cm_f = cli_opts()
        if not cm_f: st.warning("No hay clientes."); st.stop()
        cli_f = st.selectbox("Cliente", list(cm_f.keys()), key="cli_f")

    cid_f   = cm_f[cli_f]
    res_all = svc.reporte_mensual_cliente(db, mes_f, anio_f)
    res_cli = next((r for r in res_all if r["cliente_id"] == cid_f), None)

    if not res_cli:
        st.info(f"No hay actividad facturable en {MESES[mes_f-1]} {anio_f}.")
    else:
        sec(f"{res_cli['empresa']}  ·  {res_cli['cliente']}", f"{MESES[mes_f-1]} {anio_f}")

        f1, f2, f3 = st.columns(3)
        f1.metric("Tarifa",             res_cli["tarifa"])
        f2.metric("Condiciones pago",   res_cli["condiciones_pago"])
        f3.metric("Pallets en almacén", res_cli["pallets_almacenados"])

        st.markdown("---")
        d1, d2, d3, d4, d5 = st.columns(5)
        d1.metric("Almacenaje",   f"{res_cli['total_almacenaje']:.2f} €")
        d2.metric("Preparación",  f"{res_cli['picking_coste']:.2f} €")
        d3.metric("Cargas",       f"{res_cli['cargas_coste']:.2f} €")
        d4.metric("Descargas",    f"{res_cli['descargas_coste']:.2f} €")
        d5.metric("Distribución", f"{res_cli['distribucion_coste']:.2f} €")

        st.markdown(f"""
        <div class="total-box">
            <div class="label">TOTAL A FACTURAR · {MESES[mes_f-1].upper()} {anio_f}</div>
            <div class="amount">{res_cli['total']:,.2f} €</div>
        </div>""", unsafe_allow_html=True)

        det_alm = [r for r in svc.reporte_almacenaje(db, mes_f, anio_f)
                   if r["cliente"] == res_cli["cliente"]]
        det_ops = [o for o in svc.reporte_operaciones(db, mes_f, anio_f)
                   if o["cliente"] == res_cli["cliente"]]
        pdf_fact = pdf_gen.generar_pdf_factura_cliente(res_cli, mes_f, anio_f, det_alm, det_ops)
        st.download_button(
            f"⬇  Descargar factura PDF — {res_cli['empresa']}",
            data=pdf_fact,
            file_name=f"factura_{res_cli['empresa'].replace(' ', '_')}_{anio_f}_{mes_f:02d}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
