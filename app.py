"""
app.py — WMS ONUS EXPRESS v2
Branding completo · Tarifas editables · Títulos en todos los campos
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

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
LOGO_W = _b64(os.path.join(ASSETS, "logo_white.png"))
LOGO_C = _b64(os.path.join(ASSETS, "logo_color.png"))

# ─── Config ──────────────────────────────────────────────────
st.set_page_config(page_title="WMS · ONUS EXPRESS", page_icon="🚚",
                   layout="wide", initial_sidebar_state="expanded")

# ─── CSS ONUS EXPRESS ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=REM:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family:'REM',sans-serif !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#000935 0%,#001560 100%) !important;
    border-right: 2px solid #00C9CE;
}
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color:#e0f7f8 !important;
    font-family:'REM',sans-serif !important;
    font-size:0.88rem !important;
}
.sidebar-brand {
    padding:1.2rem 1rem 0.8rem;
    text-align:center;
    border-bottom:1px solid #00C9CE44;
    margin-bottom:0.8rem;
}
.sidebar-brand img { width:150px; max-width:90%; }
.sidebar-brand-text {
    color:#00C9CE;
    font-size:0.65rem;
    letter-spacing:3px;
    text-transform:uppercase;
    margin-top:0.4rem;
    font-weight:600;
}

/* Header */
.onus-header {
    background: linear-gradient(135deg,#000935 0%,#001a6e 60%,#003080 100%);
    padding:1.4rem 2rem 1.2rem;
    border-radius:10px;
    margin-bottom:1.2rem;
    border-bottom:3px solid #00C9CE;
    display:flex; flex-direction:column;
    align-items:center; text-align:center; gap:0.4rem;
}
.onus-header img   { height:52px; }
.onus-header-wms   { color:#00C9CE; font-size:0.75rem; font-weight:700;
                     letter-spacing:3px; text-transform:uppercase; margin:0; }
.onus-header-page  { color:#94b4d4; font-size:0.7rem; letter-spacing:2px;
                     text-transform:uppercase; margin:0; }

/* KPI */
.kpi-card {
    background:#fff; border:1px solid #e0f7f8;
    border-top:3px solid #00C9CE; border-radius:8px;
    padding:1rem 1.2rem; text-align:center;
}
.kpi-value { font-size:1.9rem; font-weight:700; color:#000935; line-height:1; }
.kpi-label { font-size:0.7rem; color:#5a6a85; margin-top:0.3rem;
             text-transform:uppercase; letter-spacing:.7px; }

/* Section title */
.sec-title {
    font-size:1.05rem; font-weight:700; color:#000935;
    padding:0.3rem 0; border-bottom:2px solid #00C9CE;
    margin-bottom:0.9rem;
}
.sec-sub { font-size:0.8rem; color:#5a6a85; margin:-0.6rem 0 0.9rem; }

/* Forms */
div[data-testid="stForm"] {
    background:#f8fafc; border-radius:8px;
    padding:1.2rem; border:1px solid #e2e8f0;
}
.field-label {
    font-size:0.78rem; font-weight:600; color:#000935;
    text-transform:uppercase; letter-spacing:.5px;
    margin-bottom:4px;
}

/* Buttons */
.stButton>button {
    border-radius:6px; font-weight:600;
    font-family:'REM',sans-serif;
    background:#000935; color:white; border:none;
}
.stButton>button:hover { background:#00C9CE !important; color:#000935 !important; }

/* Tabs */
.stTabs [data-baseweb="tab"] {
    background:#f0f9ff; border-radius:6px 6px 0 0;
    font-family:'REM',sans-serif; font-size:0.82rem; color:#000935; font-weight:500;
}
.stTabs [aria-selected="true"] { background:#000935 !important; color:#00C9CE !important; }

/* Metric */
[data-testid="metric-container"] {
    background:white; border:1px solid #e0f7f8;
    border-top:3px solid #00C9CE; border-radius:8px; padding:.7rem;
}

/* Total highlight */
.total-box {
    background:#000935; color:white;
    padding:1.1rem 2rem; border-radius:8px;
    border-left:4px solid #00C9CE; margin:1rem 0;
}
.total-box .label { font-size:0.75rem; color:#00C9CE; letter-spacing:2px;
                    text-transform:uppercase; }
.total-box .amount { font-size:2rem; font-weight:700; font-family:'REM',sans-serif; }

/* Info pill */
.precio-info {
    background:#e0f7f8; border-left:3px solid #00C9CE;
    border-radius:0 6px 6px 0; padding:8px 14px;
    font-size:0.83rem; color:#004a4d;
}
.precio-personalizado {
    background:#fef9c3; border-left:3px solid #ca8a04;
    border-radius:0 6px 6px 0; padding:8px 14px;
    font-size:0.83rem; color:#854d0e;
}
</style>
""", unsafe_allow_html=True)

# ─── Constantes ──────────────────────────────────────────────
TIPOS_LABEL = {
    "almacenaje":           "📦 Almacenaje",
    "picking":              "🔍 Picking",
    "empaquetado":          "🎁 Empaquetado",
    "carga":                "🚛 Carga",
    "descarga":             "🏭 Descarga",
    "distribucion-interna": "🚐 Distribución Interna",
    "distribucion-externa": "✈️  Distribución Externa",
}
GRUPOS_OP = {
    "📦 Almacenaje":             ["almacenaje"],
    "📋 Preparación de pedidos": ["picking","empaquetado"],
    "🚛 Cargas / Descargas":     ["carga","descarga"],
    "🚚 Distribución":           ["distribucion-interna","distribucion-externa"],
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
        st.error(f"❌ Error de conexión: {e}")
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

# ─── Header ──────────────────────────────────────────────────
def header(pagina: str, subtitulo: str = ""):
    if LOGO_W:
        logo_tag = f'<img src="data:image/png;base64,{LOGO_W}" style="height:52px;">'
    else:
        logo_tag = '<span style="color:white;font-size:1.4rem;font-weight:800;letter-spacing:2px;">ONUS EXPRESS</span>'
    sub_txt = pagina.upper() + (" &nbsp;·&nbsp; " + subtitulo.upper() if subtitulo else "")
    st.markdown(f"""<div class="onus-header">
        {logo_tag}
        <p class="onus-header-wms">WMS &nbsp;·&nbsp; ONUS EXPRESS</p>
        <p class="onus-header-page">{sub_txt}</p>
    </div>""", unsafe_allow_html=True)

def sec(titulo, subtitulo=""):
    st.markdown(f"<div class='sec-title'>{titulo}</div>", unsafe_allow_html=True)
    if subtitulo:
        st.markdown(f"<div class='sec-sub'>{subtitulo}</div>", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    if LOGO_W:
        st.markdown(f'''<div class="sidebar-brand">
            <img src="data:image/png;base64,{LOGO_W}" style="width:150px;max-width:90%;">
            <div class="sidebar-brand-text">Warehouse Management</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown('''<div class="sidebar-brand">
            <span style="color:#00C9CE;font-size:1.1rem;font-weight:800;letter-spacing:2px;">ONUS EXPRESS</span>
            <div class="sidebar-brand-text">Warehouse Management</div>
        </div>''', unsafe_allow_html=True)

    pagina = st.radio("", [
        "🏠 Dashboard","👥 Clientes","💰 Tarifas",
        "📋 Operaciones","📦 Stock","📊 Reportes","🧾 Facturación"
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"<small style='color:#00C9CE'>📅 {date.today().strftime('%d/%m/%Y')}</small>",
                unsafe_allow_html=True)

pag = pagina.split(" ",1)[1]

# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
if pag == "Dashboard":
    header("Dashboard", "Gestión de operaciones de almacén")
    refresh_db()
    try:
        kpis = svc.get_kpis_dashboard(db)
    except Exception as e:
        st.error(f"Error: {e}"); st.stop()

    c1,c2,c3,c4,c5 = st.columns(5)
    for col,val,label,icon in [
        (c1, kpis["total_clientes"],           "Clientes activos",    "👥"),
        (c2, kpis["pallets_activos"],           "Pallets en almacén",  "📦"),
        (c3, kpis["ops_mes"],                   "Operaciones este mes", "⚡"),
        (c4, f"{kpis['facturacion_mes']:,.2f}€","Facturación mes",     "📈"),
        (c5, f"{kpis['total_facturado']:,.2f}€","Facturación total",   "💰"),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-card">
                <div style="font-size:1.4rem">{icon}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns(2)
    with cl:
        sec("Últimas operaciones")
        movs = svc.get_all_movimientos(db)[:12]
        if movs:
            rows = []
            for m in movs:
                c_ = svc.get_cliente_by_id(db, m.cliente_id)
                rows.append({"Fecha": m.fecha.strftime("%d/%m/%Y"),
                             "Cliente": c_.nombre if c_ else "—",
                             "Tipo de servicio": TIPOS_LABEL.get(m.tipo, m.tipo),
                             "Cantidad": float(m.cantidad),
                             "Coste €": f"{float(m.coste or 0):.2f}"})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("Sin operaciones registradas.")

    with cr:
        sec("Stock activo")
        stock = svc.get_stock_activo(db)[:12]
        if stock:
            rows = []
            for s in stock:
                c_ = svc.get_cliente_by_id(db, s.cliente_id)
                rows.append({"Cliente": c_.nombre if c_ else "—",
                             "Pallet": s.pallet, "Referencia": s.referencia or "—",
                             "F. Entrada": s.fecha_entrada.strftime("%d/%m/%Y"),
                             "Días": (date.today()-s.fecha_entrada).days})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No hay pallets en almacén.")

# ══════════════════════════════════════════════════════════════
# CLIENTES
# ══════════════════════════════════════════════════════════════
elif pag == "Clientes":
    header("Clientes", "Alta, edición y condiciones comerciales")
    refresh_db()

    tab_lista, tab_nuevo, tab_editar, tab_tarifa_esp = st.tabs(
        ["📋 Listado", "➕ Nuevo Cliente", "✏️ Editar / Eliminar", "⭐ Tarifa Especial"])

    with tab_lista:
        sec("Listado de clientes", "Todos los clientes registrados en el sistema")
        clientes = svc.get_all_clientes(db)
        if clientes:
            data = [{"ID": c.id, "Empresa": c.empresa or "—", "Contacto": c.nombre,
                     "Email": c.email or "—", "Teléfono": c.telefono or "—",
                     "Tarifa asignada": c.tarifa.nombre if c.tarifa else "⚠️ Sin tarifa",
                     "Condiciones de pago": c.condiciones_pago or "—"} for c in clientes]
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(clientes)} clientes")
        else:
            st.info("No hay clientes registrados. Usa la pestaña 'Nuevo Cliente' para añadir el primero.")

    with tab_nuevo:
        sec("Nuevo cliente", "Rellena todos los campos para dar de alta un cliente")
        tm = tar_opts()
        with st.form("form_nuevo_cli", clear_on_submit=True):
            st.markdown("**Datos de la empresa**")
            col1, col2 = st.columns(2)
            with col1:
                empresa  = st.text_input("Empresa / Razón social *", placeholder="Ej. Distribuciones García S.L.")
                nombre   = st.text_input("Persona de contacto *",    placeholder="Ej. Juan García")
                email    = st.text_input("Email de contacto",        placeholder="juan@empresa.com")
            with col2:
                telefono = st.text_input("Teléfono",                 placeholder="612 345 678")
                cond     = st.selectbox("Condiciones de pago",       COND_PAGO)
                tar_sel  = st.selectbox("Tarifa asignada",           ["Sin tarifa"]+list(tm.keys()),
                                        help="Define los precios que se aplicarán a este cliente")
            if st.form_submit_button("💾 Guardar nuevo cliente", type="primary", use_container_width=True):
                if not empresa.strip() or not nombre.strip():
                    st.error("⚠️ Empresa y persona de contacto son obligatorios.")
                else:
                    tid = tm.get(tar_sel) if tar_sel != "Sin tarifa" else None
                    svc.create_cliente(db, {"nombre": nombre.strip(), "empresa": empresa.strip(),
                                            "email": email.strip() or None, "telefono": telefono.strip() or None,
                                            "condiciones_pago": cond, "tarifa_id": tid})
                    st.success(f"✅ Cliente '{empresa}' creado correctamente.")
                    st.rerun()

    with tab_editar:
        sec("Editar o eliminar cliente")
        clientes = svc.get_all_clientes(db)
        if not clientes:
            st.info("No hay clientes.")
        else:
            cm = {f"{c.empresa or '—'} · {c.nombre}": c.id for c in clientes}
            sel = st.selectbox("Selecciona el cliente a modificar", list(cm.keys()))
            c   = svc.get_cliente_by_id(db, cm[sel])
            tm  = tar_opts()
            if c:
                st.markdown("---")
                with st.form("form_edit_cli"):
                    st.markdown("**Datos de la empresa**")
                    col1, col2 = st.columns(2)
                    with col1:
                        emp_e  = st.text_input("Empresa / Razón social *", value=c.empresa or "")
                        nom_e  = st.text_input("Persona de contacto *",    value=c.nombre)
                        eml_e  = st.text_input("Email de contacto",        value=c.email or "")
                    with col2:
                        tel_e  = st.text_input("Teléfono",                 value=c.telefono or "")
                        ci     = COND_PAGO.index(c.condiciones_pago) if c.condiciones_pago in COND_PAGO else 0
                        cnd_e  = st.selectbox("Condiciones de pago",       COND_PAGO, index=ci)
                        tns    = ["Sin tarifa"]+list(tm.keys())
                        ta     = c.tarifa.nombre if c.tarifa else "Sin tarifa"
                        ti     = tns.index(ta) if ta in tns else 0
                        tar_e  = st.selectbox("Tarifa asignada",           tns, index=ti)

                    cg, cd = st.columns([3,1])
                    with cg: guardar   = st.form_submit_button("💾 Actualizar cliente", type="primary", use_container_width=True)
                    with cd: eliminar  = st.form_submit_button("🗑️ Eliminar",           use_container_width=True)

                    if guardar:
                        tid = tm.get(tar_e) if tar_e != "Sin tarifa" else None
                        svc.update_cliente(db, c.id, {"nombre": nom_e, "empresa": emp_e or None,
                                                       "email": eml_e or None, "telefono": tel_e or None,
                                                       "condiciones_pago": cnd_e, "tarifa_id": tid})
                        st.success("✅ Cliente actualizado."); st.rerun()
                    if eliminar:
                        svc.delete_cliente(db, c.id)
                        st.warning("🗑️ Cliente eliminado."); st.rerun()

    with tab_tarifa_esp:
        sec("Tarifa especial por cliente",
            "Precios negociados que sobreescriben la tarifa general del cliente")
        clientes = svc.get_all_clientes(db)
        if not clientes:
            st.info("No hay clientes.")
        else:
            cm2 = {f"{c.empresa or '—'} · {c.nombre}": c.id for c in clientes}
            sel2 = st.selectbox("Cliente", list(cm2.keys()), key="cli_tar_esp")
            cid2 = cm2[sel2]
            c2   = svc.get_cliente_by_id(db, cid2)

            # Tarifa general actual
            if c2 and c2.tarifa:
                st.info(f"📋 Tarifa general asignada: **{c2.tarifa.nombre}**  "
                        f"— Los precios especiales aquí tienen prioridad sobre esa tarifa.")

            # Mostrar precios especiales existentes
            tcs = svc.get_tarifas_cliente(db, cid2)
            if tcs:
                st.markdown("**Precios especiales activos:**")
                rows_tc = [{"ID": t.id, "Tipo de servicio": TIPOS_LABEL.get(t.tipo_servicio, t.tipo_servicio),
                            "Tipo de cálculo": svc.CALCULO_LABEL.get(t.tipo_calculo, t.tipo_calculo),
                            "Precio €": float(t.precio), "Descripción": t.descripcion or "—"} for t in tcs]
                st.dataframe(pd.DataFrame(rows_tc), use_container_width=True, hide_index=True)

                col_del1, col_del2 = st.columns([2,1])
                with col_del1:
                    id_del_tc = st.number_input("ID de precio especial a eliminar", min_value=1, step=1)
                with col_del2:
                    if st.button("🗑️ Eliminar precio especial"):
                        svc.delete_tarifa_cliente(db, int(id_del_tc))
                        st.success("Eliminado."); st.rerun()
            else:
                st.info("Este cliente no tiene precios especiales — se aplica la tarifa general.")

            st.markdown("---")
            st.markdown("**Añadir / editar precio especial:**")
            with st.form("form_tar_esp", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    tipo_srv = st.selectbox("Tipo de servicio *",
                                            [TIPOS_LABEL[t] for t in svc.TIPOS_SERVICIO])
                    tipo_srv_key = svc.TIPOS_SERVICIO[[TIPOS_LABEL[t] for t in svc.TIPOS_SERVICIO].index(tipo_srv)]
                with col2:
                    tipo_calc = st.selectbox("Tipo de cálculo *",
                                             list(svc.CALCULO_LABEL.values()))
                    tipo_calc_key = svc.CALCULO_OPTS[list(svc.CALCULO_LABEL.values()).index(tipo_calc)]
                with col3:
                    precio_esp = st.number_input("Precio € *", min_value=0.0, step=0.05, format="%.2f")

                desc_esp = st.text_input("Descripción / nota interna", placeholder="Ej. Precio acordado en contrato 2025")
                if st.form_submit_button("💾 Guardar precio especial", type="primary", use_container_width=True):
                    svc.upsert_tarifa_cliente(db, cid2, tipo_srv_key, tipo_calc_key, precio_esp, desc_esp)
                    st.success(f"✅ Precio especial guardado para {tipo_srv}."); st.rerun()

# ══════════════════════════════════════════════════════════════
# TARIFAS
# ══════════════════════════════════════════════════════════════
elif pag == "Tarifas":
    header("Tarifas", "Configuración de precios por tipo de servicio")
    refresh_db()

    tab_lista, tab_nueva, tab_detalle = st.tabs(
        ["📋 Tarifas", "➕ Nueva Tarifa", "⚙️ Precios por Servicio"])

    with tab_lista:
        sec("Tarifas disponibles", "Resumen de todas las tarifas configuradas")
        tarifas = svc.get_all_tarifas(db)
        if tarifas:
            for t in tarifas:
                with st.expander(f"📋 {t.nombre}"):
                    detalles = svc.get_detalles_tarifa(db, t.id)
                    if detalles:
                        rows = [{"Tipo de servicio": TIPOS_LABEL.get(d.tipo_servicio, d.tipo_servicio),
                                 "Tipo de cálculo": svc.CALCULO_LABEL.get(d.tipo_calculo, d.tipo_calculo),
                                 "Precio €": float(d.precio),
                                 "Descripción": d.descripcion or "—"} for d in detalles]
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    else:
                        st.caption("Sin precios detallados configurados — usando precios legacy.")
                        st.write(f"Almacenaje: **{float(t.precio_pallet_dia):.2f} €/día**  |  "
                                 f"Picking: **{float(t.precio_picking):.2f} €/ud**  |  "
                                 f"Carga: **{float(t.precio_carga):.2f} €**  |  "
                                 f"Descarga: **{float(t.precio_descarga):.2f} €**")

                    col_del = st.columns([4,1])[1]
                    with col_del:
                        if st.button(f"🗑️ Eliminar", key=f"del_tar_{t.id}"):
                            svc.delete_tarifa(db, t.id)
                            st.warning("Tarifa eliminada."); st.rerun()
        else:
            st.info("No hay tarifas. Crea la primera en la pestaña 'Nueva Tarifa'.")

    with tab_nueva:
        sec("Crear nueva tarifa", "Define un nombre y los precios base por tipo de servicio")
        with st.form("form_nueva_tar", clear_on_submit=True):
            nombre_t = st.text_input("Nombre de la tarifa *",
                                     placeholder="Ej. Tarifa Estándar 2025 · Clientes Premium")
            st.markdown("**Precios base por tipo de servicio:**")
            st.caption("Podrás editar estos precios en detalle desde la pestaña 'Precios por Servicio'")

            col1,col2,col3,col4 = st.columns(4)
            with col1: pp = st.number_input("📦 Almacenaje €/pallet/día", min_value=0.0, step=0.05, value=0.75, format="%.2f")
            with col2: pk = st.number_input("🔍 Picking / Empaquet. €/ud", min_value=0.0, step=0.05, value=1.50, format="%.2f")
            with col3: pc = st.number_input("🚛 Carga €/operación",        min_value=0.0, step=1.0,  value=35.0, format="%.2f")
            with col4: pd_= st.number_input("🏭 Descarga €/operación",     min_value=0.0, step=1.0,  value=35.0, format="%.2f")

            if st.form_submit_button("💾 Crear tarifa", type="primary", use_container_width=True):
                if not nombre_t.strip():
                    st.error("⚠️ El nombre es obligatorio.")
                else:
                    t = svc.create_tarifa(db, {"nombre": nombre_t.strip(), "precio_pallet_dia": pp,
                                                "precio_picking": pk, "precio_carga": pc, "precio_descarga": pd_})
                    # Crear detalles automáticamente
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
                    st.success(f"✅ Tarifa '{nombre_t}' creada con todos los precios."); st.rerun()

    with tab_detalle:
        sec("Editar precios por servicio",
            "Ajusta individualmente el precio de cada tipo de operación para cada tarifa")
        tarifas = svc.get_all_tarifas(db)
        if not tarifas:
            st.info("Primero crea una tarifa.")
        else:
            tm2 = {t.nombre: t.id for t in tarifas}
            sel_t = st.selectbox("Selecciona la tarifa a editar", list(tm2.keys()))
            tar_id = tm2[sel_t]
            detalles = svc.get_detalles_tarifa(db, tar_id)

            # Mostrar y editar cada tipo de servicio
            st.markdown("**Configura el precio para cada tipo de servicio:**")
            det_map = {d.tipo_servicio: d for d in detalles}

            with st.form("form_detalle_tar"):
                filas = []
                for tipo in svc.TIPOS_SERVICIO:
                    d = det_map.get(tipo)
                    col1, col2, col3 = st.columns([3,2,2])
                    with col1:
                        st.markdown(f"<div class='field-label'>{TIPOS_LABEL[tipo]}</div>",
                                    unsafe_allow_html=True)
                        desc_v = st.text_input(f"Descripción", value=d.descripcion or "" if d else "",
                                               key=f"desc_{tipo}", label_visibility="collapsed",
                                               placeholder="Descripción interna...")
                    with col2:
                        calcs  = list(svc.CALCULO_LABEL.values())
                        c_idx  = calcs.index(svc.CALCULO_LABEL.get(d.tipo_calculo, "por_unidad")) if d else 0
                        calc_v = st.selectbox("Tipo cálculo", calcs, index=c_idx,
                                              key=f"calc_{tipo}", label_visibility="collapsed")
                    with col3:
                        prec_v = st.number_input("Precio €", min_value=0.0, step=0.05,
                                                 value=float(d.precio) if d else 0.0,
                                                 format="%.2f", key=f"prec_{tipo}",
                                                 label_visibility="collapsed")
                    filas.append((tipo, calc_v, prec_v, desc_v))

                if st.form_submit_button("💾 Guardar todos los precios", type="primary", use_container_width=True):
                    for tipo, calc_lbl, precio, desc in filas:
                        calc_key = svc.CALCULO_OPTS[list(svc.CALCULO_LABEL.values()).index(calc_lbl)]
                        svc.upsert_detalle_tarifa(db, tar_id, tipo, calc_key, precio, desc)
                    st.success(f"✅ Precios de '{sel_t}' actualizados correctamente.")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
# OPERACIONES
# ══════════════════════════════════════════════════════════════
elif pag == "Operaciones":
    header("Registro de operaciones", "Introduce la actividad realizada")
    refresh_db()

    tab_nuevo, tab_hist = st.tabs(["➕ Nueva Operación", "📜 Historial de operaciones"])

    with tab_nuevo:
        sec("Nueva operación", "Selecciona el cliente, el tipo de servicio y la cantidad")
        cm = cli_opts()
        if not cm:
            st.warning("⚠️ Primero debes crear clientes en la sección Clientes.")
        else:
            # Grupo primero para filtrar tipos
            grupo = st.selectbox("Grupo de operación", list(GRUPOS_OP.keys()),
                                 help="Selecciona la categoría de la operación")

            with st.form("form_op", clear_on_submit=True):
                st.markdown("**Datos de la operación:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    cli_sel = st.selectbox("Cliente *", list(cm.keys()),
                                           help="Empresa a la que se facturará esta operación")
                    tipos_g  = GRUPOS_OP[grupo]
                    tipo_lbs = [TIPOS_LABEL[t] for t in tipos_g]
                    tipo_lb  = st.selectbox("Tipo de servicio *", tipo_lbs,
                                            help="Operación específica realizada")
                    tipo_key = tipos_g[tipo_lbs.index(tipo_lb)]
                with col2:
                    cantidad = st.number_input("Cantidad *", min_value=0.01, step=1.0, value=1.0,
                                               format="%.2f",
                                               help="Unidades, pallets u operaciones realizadas")
                    fecha_op = st.date_input("Fecha de la operación *", value=date.today())
                with col3:
                    obs = st.text_area("Observaciones",
                                       placeholder="Número de pedido, albarán, referencia...",
                                       height=108)

                # Preview precio con fuente
                cid_prev = cm.get(cli_sel)
                if cid_prev:
                    info = svc.resolver_precio(db, cid_prev, tipo_key)
                    coste_est = svc.calcular_coste(info["precio"], info["tipo_calculo"], float(cantidad))
                    fuente_txt = {"personalizada": "⭐ Precio especial negociado",
                                  "tarifa_general": "📋 Tarifa general asignada",
                                  "legacy":         "📋 Tarifa base",
                                  "sin_tarifa":     "⚠️ Sin tarifa — coste será 0 €"}.get(info["fuente"],"")
                    css_cls = "precio-personalizado" if info["fuente"] == "personalizada" else "precio-info"
                    st.markdown(f"""<div class="{css_cls}">
                        💡 Coste estimado: <b>{coste_est:.2f} €</b> &nbsp;·&nbsp;
                        {svc.CALCULO_LABEL.get(info["tipo_calculo"],"")} a {info["precio"]:.2f} €
                        &nbsp;·&nbsp; {fuente_txt}
                    </div>""", unsafe_allow_html=True)

                if st.form_submit_button("✅ Registrar operación", type="primary", use_container_width=True):
                    svc.create_movimiento(db, {"cliente_id": cm[cli_sel], "tipo": tipo_key,
                                               "cantidad": cantidad, "fecha": fecha_op,
                                               "observaciones": obs.strip() or None})
                    st.success(f"✅ Operación '{tipo_lb}' registrada correctamente.")
                    st.rerun()

    with tab_hist:
        sec("Historial de operaciones", "Filtra por cliente, tipo y período")
        col1,col2,col3,col4 = st.columns(4)
        with col1:
            cm2 = {"Todos los clientes": None} | cli_opts()
            f_cli = st.selectbox("Cliente", list(cm2.keys()))
        with col2:
            f_grp = st.selectbox("Grupo de operación", ["Todos"]+list(GRUPOS_OP.keys()))
        with col3:
            f_desde = st.date_input("Desde", value=date.today()-timedelta(days=30))
        with col4:
            f_hasta = st.date_input("Hasta", value=date.today())

        tipos_f = GRUPOS_OP.get(f_grp) if f_grp != "Todos" else None
        movs = svc.get_all_movimientos(db, cliente_id=cm2.get(f_cli),
                                        fecha_desde=f_desde, fecha_hasta=f_hasta)
        if tipos_f:
            movs = [m for m in movs if m.tipo in tipos_f]

        if movs:
            rows = []
            for m in movs:
                c_ = svc.get_cliente_by_id(db, m.cliente_id)
                rows.append({"ID": m.id, "Fecha": m.fecha.strftime("%d/%m/%Y"),
                             "Cliente": c_.nombre if c_ else "—",
                             "Empresa": c_.empresa if c_ else "—",
                             "Tipo de servicio": TIPOS_LABEL.get(m.tipo, m.tipo),
                             "Cantidad": float(m.cantidad),
                             "Coste €": float(m.coste or 0),
                             "Observaciones": (m.observaciones or "")[:60]})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            c1,c2,c3 = st.columns(3)
            c1.metric("Total operaciones", len(movs))
            c2.metric("Unidades totales", int(sum(float(m.cantidad) for m in movs)))
            c3.metric("Coste total", f"{sum(float(m.coste or 0) for m in movs):,.2f} €")

            st.markdown("---")
            st.markdown("**Eliminar operación por ID:**")
            ci, cb = st.columns([2,1])
            with ci: id_del = st.number_input("ID de operación", min_value=1, step=1)
            with cb:
                if st.button("🗑️ Eliminar"):
                    if svc.delete_movimiento(db, int(id_del)):
                        st.success("Eliminada."); st.rerun()
                    else: st.error("ID no encontrado.")
        else:
            st.info("No hay operaciones con los filtros seleccionados.")

# ══════════════════════════════════════════════════════════════
# STOCK
# ══════════════════════════════════════════════════════════════
elif pag == "Stock":
    header("Stock", "Pallets en almacén · Entradas y salidas")
    refresh_db()

    tab_act, tab_ent, tab_sal = st.tabs(["📦 Stock Activo","📥 Entrada de Pallet","📤 Dar Salida"])

    with tab_act:
        sec("Pallets activos en almacén", "Todos los pallets que están actualmente almacenados")
        cm_s = {"Todos los clientes": None} | cli_opts()
        f_s  = st.selectbox("Filtrar por cliente", list(cm_s.keys()))
        stck = svc.get_stock_activo(db, cliente_id=cm_s.get(f_s))
        if stck:
            rows = []
            for s in stck:
                c_ = svc.get_cliente_by_id(db, s.cliente_id)
                dias = (date.today()-s.fecha_entrada).days
                info = svc.resolver_precio(db, s.cliente_id, "almacenaje")
                rows.append({"ID": s.id, "Empresa": c_.empresa if c_ else "—",
                             "Cliente": c_.nombre if c_ else "—",
                             "Pallet": s.pallet, "Referencia": s.referencia or "—",
                             "Cantidad": s.cantidad,
                             "F. Entrada": s.fecha_entrada.strftime("%d/%m/%Y"),
                             "Días": dias,
                             "Coste acum. €": round(dias * info["precio"] * s.cantidad, 2)})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            c1,c2 = st.columns(2)
            c1.metric("Pallets activos", len(stck))
            c2.metric("Coste acumulado", f"{sum(r['Coste acum. €'] for r in rows):,.2f} €")
        else:
            st.info("No hay pallets en almacén.")

    with tab_ent:
        sec("Registrar entrada de pallet", "Introduce los datos del pallet que entra al almacén")
        cm_e = cli_opts()
        if not cm_e:
            st.warning("Crea clientes primero.")
        else:
            with st.form("form_ent", clear_on_submit=True):
                col1,col2 = st.columns(2)
                with col1:
                    cli_e = st.selectbox("Cliente *", list(cm_e.keys()),
                                         help="Cliente propietario de la mercancía")
                    pal_e = st.text_input("Código de pallet *", placeholder="Ej. PAL-001",
                                          help="Identificador único del pallet")
                    ref_e = st.text_input("Referencia / Artículo",   placeholder="Ej. REF-X100")
                with col2:
                    qty_e = st.number_input("Número de pallets", min_value=1, step=1, value=1)
                    fec_e = st.date_input("Fecha de entrada *", value=date.today())
                    obs_e = st.text_input("Observaciones", placeholder="Nº albarán, proveedor...")

                if st.form_submit_button("📥 Registrar entrada", type="primary", use_container_width=True):
                    if not pal_e.strip():
                        st.error("⚠️ El código de pallet es obligatorio.")
                    else:
                        svc.create_stock(db, {"cliente_id": cm_e[cli_e], "pallet": pal_e.strip(),
                                              "referencia": ref_e.strip() or None, "cantidad": qty_e,
                                              "fecha_entrada": fec_e,
                                              "observaciones": obs_e.strip() or None, "activo": True})
                        st.success(f"✅ Pallet '{pal_e}' registrado en almacén."); st.rerun()

    with tab_sal:
        sec("Dar salida a un pallet", "Selecciona el pallet que sale del almacén")
        sa = svc.get_stock_activo(db)
        if not sa:
            st.info("No hay pallets activos para dar salida.")
        else:
            pm = {}
            for s in sa:
                c_ = svc.get_cliente_by_id(db, s.cliente_id)
                pm[f"ID:{s.id} · {s.pallet} · {c_.empresa if c_ else '—'} · entrada {s.fecha_entrada.strftime('%d/%m/%Y')}"] = s.id
            sel_p  = st.selectbox("Pallet a retirar", list(pm.keys()))
            fec_sal = st.date_input("Fecha de salida", value=date.today())
            if st.button("📤 Confirmar salida de almacén", type="primary"):
                svc.dar_salida_pallet(db, pm[sel_p], fec_sal)
                st.success("✅ Pallet dado de baja."); st.rerun()

# ══════════════════════════════════════════════════════════════
# REPORTES
# ══════════════════════════════════════════════════════════════
elif pag == "Reportes":
    header("Reportes", "Análisis de actividad y facturación")
    refresh_db()

    hoy = date.today()
    col_m, col_a = st.columns(2)
    with col_m: mes = st.selectbox("Mes", range(1,13), index=hoy.month-1, format_func=lambda x: MESES[x-1])
    with col_a: anio = st.selectbox("Año", range(2023, hoy.year+2), index=hoy.year-2023)

    tab_alm,tab_prep,tab_cd,tab_dist,tab_men = st.tabs([
        "📦 Almacenaje","📋 Preparación","🚛 Cargas/Descargas","🚚 Distribución","📊 Resumen Mensual"])

    with tab_alm:
        sec("Informe de almacenaje", f"{MESES[mes-1]} {anio}")
        rows = svc.reporte_almacenaje(db, mes, anio)
        if rows:
            df = pd.DataFrame([{"Cliente": r["cliente"],"Empresa": r["empresa"],
                                "Pallet": r["pallet"],"Referencia": r["referencia"],
                                "F. Entrada": r["fecha_entrada"].strftime("%d/%m/%Y"),
                                "F. Salida": r["fecha_salida"].strftime("%d/%m/%Y") if r.get("fecha_salida") else "En almacén",
                                "Días": r["dias"],"€/día": r["precio_dia"],"Total €": r["coste"]} for r in rows])
            st.dataframe(df, use_container_width=True, hide_index=True)
            c1,c2 = st.columns(2)
            c1.metric("Pallets facturados", len(rows))
            c2.metric("Total almacenaje", f"{sum(r['coste'] for r in rows):,.2f} €")
            pdf_b = pdf_gen.generar_pdf_almacenaje(rows, mes, anio)
            st.download_button("⬇️ Descargar PDF Almacenaje", data=pdf_b,
                               file_name=f"almacenaje_{anio}_{mes:02d}.pdf", mime="application/pdf", type="primary")
        else:
            st.info("Sin datos de almacenaje en este período.")

    with tab_prep:
        sec("Preparación de pedidos", f"Picking y empaquetado · {MESES[mes-1]} {anio}")
        rows = []
        for t in ["picking","empaquetado"]: rows += svc.reporte_operaciones(db, mes, anio, t)
        rows.sort(key=lambda x: x["fecha"], reverse=True)
        if rows:
            df = pd.DataFrame([{"ID": r["id"],"Fecha": r["fecha"].strftime("%d/%m/%Y"),
                                "Cliente": r["cliente"],"Tipo": TIPOS_LABEL.get(r["tipo"],r["tipo"]),
                                "Cantidad": r["cantidad"],"Coste €": r["coste"],
                                "Obs.": r["observaciones"][:50]} for r in rows])
            st.dataframe(df, use_container_width=True, hide_index=True)
            c1,c2,c3 = st.columns(3)
            c1.metric("Operaciones", len(rows))
            c2.metric("Unidades", int(sum(r["cantidad"] for r in rows)))
            c3.metric("Coste total", f"{sum(r['coste'] for r in rows):,.2f} €")
            pdf_b = pdf_gen.generar_pdf_operaciones(rows, "picking", mes, anio)
            st.download_button("⬇️ PDF Preparación", data=pdf_b,
                               file_name=f"preparacion_{anio}_{mes:02d}.pdf", mime="application/pdf", type="primary")
        else: st.info("Sin preparaciones en este período.")

    with tab_cd:
        sec("Cargas y descargas", f"{MESES[mes-1]} {anio}")
        rows = []
        for t in ["carga","descarga"]: rows += svc.reporte_operaciones(db, mes, anio, t)
        rows.sort(key=lambda x: x["fecha"], reverse=True)
        if rows:
            df = pd.DataFrame([{"ID": r["id"],"Fecha": r["fecha"].strftime("%d/%m/%Y"),
                                "Cliente": r["cliente"],"Operación": TIPOS_LABEL.get(r["tipo"],r["tipo"]),
                                "Cantidad": r["cantidad"],"Coste €": r["coste"],
                                "Obs.": r["observaciones"][:50]} for r in rows])
            st.dataframe(df, use_container_width=True, hide_index=True)
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Cargas",   sum(1 for r in rows if r["tipo"]=="carga"))
            c2.metric("Descargas",sum(1 for r in rows if r["tipo"]=="descarga"))
            c3.metric("Unidades", int(sum(r["cantidad"] for r in rows)))
            c4.metric("Coste total",f"{sum(r['coste'] for r in rows):,.2f} €")
            pdf_b = pdf_gen.generar_pdf_operaciones(rows, "carga", mes, anio)
            st.download_button("⬇️ PDF Cargas/Descargas", data=pdf_b,
                               file_name=f"cargas_{anio}_{mes:02d}.pdf", mime="application/pdf", type="primary")
        else: st.info("Sin cargas/descargas en este período.")

    with tab_dist:
        sec("Distribución", f"{MESES[mes-1]} {anio}")
        rows = []
        for t in ["distribucion-interna","distribucion-externa"]: rows += svc.reporte_operaciones(db, mes, anio, t)
        if rows:
            df = pd.DataFrame([{"ID": r["id"],"Fecha": r["fecha"].strftime("%d/%m/%Y"),
                                "Cliente": r["cliente"],"Tipo": TIPOS_LABEL.get(r["tipo"],r["tipo"]),
                                "Cantidad": r["cantidad"],"Coste €": r["coste"],
                                "Obs.": r["observaciones"][:50]} for r in rows])
            st.dataframe(df, use_container_width=True, hide_index=True)
            c1,c2,c3 = st.columns(3)
            c1.metric("Interna", sum(1 for r in rows if r["tipo"]=="distribucion-interna"))
            c2.metric("Externa", sum(1 for r in rows if r["tipo"]=="distribucion-externa"))
            c3.metric("Coste total",f"{sum(r['coste'] for r in rows):,.2f} €")
        else: st.info("Sin distribuciones en este período.")

    with tab_men:
        sec("Resumen mensual global", f"Todos los clientes · {MESES[mes-1]} {anio}")
        res = svc.reporte_mensual_cliente(db, mes, anio)
        if res:
            df = pd.DataFrame([{"Cliente": r["cliente"],"Empresa": r["empresa"],"Tarifa": r["tarifa"],
                                "Pallets": r["pallets_almacenados"],
                                "Almacenaje €": r["total_almacenaje"],
                                "Preparación €": r["picking_coste"],
                                "Cargas €": r["cargas_coste"],
                                "Descargas €": r["descargas_coste"],
                                "Distribución €": r["distribucion_coste"],
                                "TOTAL €": r["total"]} for r in res])
            st.dataframe(df, use_container_width=True, hide_index=True)
            grand = sum(r["total"] for r in res)
            st.metric("Facturación total del mes", f"{grand:,.2f} €")
            pdf_b = pdf_gen.generar_pdf_resumen_mensual(res, mes, anio)
            st.download_button("⬇️ PDF Resumen Mensual Global", data=pdf_b,
                               file_name=f"resumen_{anio}_{mes:02d}.pdf", mime="application/pdf", type="primary")
        else: st.info("Sin actividad en este período.")

# ══════════════════════════════════════════════════════════════
# FACTURACIÓN
# ══════════════════════════════════════════════════════════════
elif pag == "Facturación":
    header("Facturación", "Resumen y PDF por cliente")
    refresh_db()

    hoy = date.today()
    col_m,col_a,col_c = st.columns(3)
    with col_m: mes_f  = st.selectbox("Mes", range(1,13), index=hoy.month-1,
                                       format_func=lambda x: MESES[x-1], key="mes_f")
    with col_a: anio_f = st.selectbox("Año", range(2023,hoy.year+2), index=hoy.year-2023, key="anio_f")
    with col_c:
        cm_f = cli_opts()
        if not cm_f: st.warning("No hay clientes."); st.stop()
        cli_f = st.selectbox("Cliente", list(cm_f.keys()), key="cli_f")

    cid_f = cm_f[cli_f]
    res_all = svc.reporte_mensual_cliente(db, mes_f, anio_f)
    res_cli = next((r for r in res_all if r["cliente_id"] == cid_f), None)

    if not res_cli:
        st.info(f"No hay actividad facturable en {MESES[mes_f-1]} {anio_f}.")
    else:
        sec(f"{res_cli['empresa']}  ·  {res_cli['cliente']}",
            f"{MESES[mes_f-1]} {anio_f}")

        c1,c2,c3 = st.columns(3)
        c1.metric("Tarifa",            res_cli["tarifa"])
        c2.metric("Condiciones pago",  res_cli["condiciones_pago"])
        c3.metric("Pallets en almacén",res_cli["pallets_almacenados"])

        st.markdown("---")
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("📦 Almacenaje",    f"{res_cli['total_almacenaje']:.2f} €")
        c2.metric("📋 Preparación",   f"{res_cli['picking_coste']:.2f} €")
        c3.metric("🚛 Cargas",        f"{res_cli['cargas_coste']:.2f} €")
        c4.metric("🏭 Descargas",     f"{res_cli['descargas_coste']:.2f} €")
        c5.metric("🚚 Distribución",  f"{res_cli['distribucion_coste']:.2f} €")

        st.markdown(f"""
        <div class="total-box">
            <div class="label">TOTAL A FACTURAR</div>
            <div class="amount">{res_cli['total']:,.2f} €</div>
        </div>""", unsafe_allow_html=True)

        det_alm = [r for r in svc.reporte_almacenaje(db, mes_f, anio_f)
                   if r["cliente"] == res_cli["cliente"]]
        det_ops = [o for o in svc.reporte_operaciones(db, mes_f, anio_f)
                   if o["cliente"] == res_cli["cliente"]]
        pdf_fact = pdf_gen.generar_pdf_factura_cliente(res_cli, mes_f, anio_f, det_alm, det_ops)
        st.download_button(
            f"⬇️ Descargar Factura PDF — {res_cli['empresa']}",
            data=pdf_fact,
            file_name=f"factura_{res_cli['empresa'].replace(' ','_')}_{anio_f}_{mes_f:02d}.pdf",
            mime="application/pdf", type="primary", use_container_width=True)
