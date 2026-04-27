"""
services.py - Lógica de negocio WMS ONUS EXPRESS v2
"""
from datetime import date, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import Cliente, Tarifa, TarifaDetalle, TarifaCliente, Movimiento, Stock

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
TIPOS_SERVICIO = [
    "almacenaje",
    "picking",
    "empaquetado",
    "carga",
    "descarga",
    "distribucion-interna",
    "distribucion-externa",
]

CALCULO_OPTS = ["por_dia", "por_mes", "por_unidad", "fijo"]

CALCULO_LABEL = {
    "por_dia":    "Por día",
    "por_mes":    "Por mes",
    "por_unidad": "Por unidad",
    "fijo":       "Precio fijo",
}

# ─────────────────────────────────────────────
# TARIFAS GENERALES
# ─────────────────────────────────────────────

def get_all_tarifas(db: Session) -> List[Tarifa]:
    return db.query(Tarifa).order_by(Tarifa.nombre).all()

def get_tarifa_by_id(db: Session, tarifa_id: int) -> Optional[Tarifa]:
    return db.query(Tarifa).filter(Tarifa.id == tarifa_id).first()

def create_tarifa(db: Session, data: dict) -> Tarifa:
    t = Tarifa(**data)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

def update_tarifa(db: Session, tarifa_id: int, data: dict) -> Optional[Tarifa]:
    t = get_tarifa_by_id(db, tarifa_id)
    if not t:
        return None
    for k, v in data.items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t

def delete_tarifa(db: Session, tarifa_id: int) -> bool:
    t = get_tarifa_by_id(db, tarifa_id)
    if not t:
        return False
    db.delete(t)
    db.commit()
    return True

# ─────────────────────────────────────────────
# TARIFAS DETALLE (precios por servicio)
# ─────────────────────────────────────────────

def get_detalles_tarifa(db: Session, tarifa_id: int) -> List[TarifaDetalle]:
    return db.query(TarifaDetalle).filter(TarifaDetalle.tarifa_id == tarifa_id).all()

def upsert_detalle_tarifa(db: Session, tarifa_id: int, tipo_servicio: str,
                           tipo_calculo: str, precio: float, descripcion: str = "") -> TarifaDetalle:
    existing = (db.query(TarifaDetalle)
                .filter(TarifaDetalle.tarifa_id == tarifa_id,
                        TarifaDetalle.tipo_servicio == tipo_servicio)
                .first())
    if existing:
        existing.tipo_calculo = tipo_calculo
        existing.precio       = precio
        existing.descripcion  = descripcion
        db.commit()
        db.refresh(existing)
        return existing
    else:
        d = TarifaDetalle(tarifa_id=tarifa_id, tipo_servicio=tipo_servicio,
                          tipo_calculo=tipo_calculo, precio=precio, descripcion=descripcion)
        db.add(d)
        db.commit()
        db.refresh(d)
        return d

def delete_detalle_tarifa(db: Session, detalle_id: int) -> bool:
    d = db.query(TarifaDetalle).filter(TarifaDetalle.id == detalle_id).first()
    if not d:
        return False
    db.delete(d)
    db.commit()
    return True

# ─────────────────────────────────────────────
# TARIFAS PERSONALIZADAS POR CLIENTE
# ─────────────────────────────────────────────

def get_tarifas_cliente(db: Session, cliente_id: int) -> List[TarifaCliente]:
    return (db.query(TarifaCliente)
            .filter(TarifaCliente.cliente_id == cliente_id,
                    TarifaCliente.activo == True)
            .all())

def upsert_tarifa_cliente(db: Session, cliente_id: int, tipo_servicio: str,
                           tipo_calculo: str, precio: float, descripcion: str = "") -> TarifaCliente:
    existing = (db.query(TarifaCliente)
                .filter(TarifaCliente.cliente_id == cliente_id,
                        TarifaCliente.tipo_servicio == tipo_servicio)
                .first())
    if existing:
        existing.tipo_calculo = tipo_calculo
        existing.precio       = precio
        existing.descripcion  = descripcion
        existing.activo       = True
        db.commit()
        db.refresh(existing)
        return existing
    else:
        tc = TarifaCliente(cliente_id=cliente_id, tipo_servicio=tipo_servicio,
                           tipo_calculo=tipo_calculo, precio=precio, descripcion=descripcion)
        db.add(tc)
        db.commit()
        db.refresh(tc)
        return tc

def delete_tarifa_cliente(db: Session, tc_id: int) -> bool:
    tc = db.query(TarifaCliente).filter(TarifaCliente.id == tc_id).first()
    if not tc:
        return False
    db.delete(tc)
    db.commit()
    return True

# ─────────────────────────────────────────────
# RESOLUCIÓN DE PRECIO (lógica central)
# ─────────────────────────────────────────────

def resolver_precio(db: Session, cliente_id: int, tipo_servicio: str) -> Dict:
    """
    Devuelve el precio y tipo_calculo aplicable a un cliente para un servicio.
    Prioridad: tarifa personalizada > tarifa_detalle de tarifa asignada > precio legacy.
    """
    # 1. Tarifa personalizada del cliente
    tc = (db.query(TarifaCliente)
          .filter(TarifaCliente.cliente_id == cliente_id,
                  TarifaCliente.tipo_servicio == tipo_servicio,
                  TarifaCliente.activo == True)
          .first())
    if tc:
        return {"precio": float(tc.precio), "tipo_calculo": tc.tipo_calculo, "fuente": "personalizada"}

    # 2. Tarifa general del cliente → buscar en tarifas_detalle
    cliente = get_cliente_by_id(db, cliente_id)
    if cliente and cliente.tarifa_id:
        td = (db.query(TarifaDetalle)
              .filter(TarifaDetalle.tarifa_id == cliente.tarifa_id,
                      TarifaDetalle.tipo_servicio == tipo_servicio)
              .first())
        if td:
            return {"precio": float(td.precio), "tipo_calculo": td.tipo_calculo, "fuente": "tarifa_general"}

        # 3. Fallback a campos legacy de la tarifa
        if cliente.tarifa:
            t = cliente.tarifa
            legacy = {
                "almacenaje":           (float(t.precio_pallet_dia), "por_dia"),
                "picking":              (float(t.precio_picking),    "por_unidad"),
                "empaquetado":          (float(t.precio_picking),    "por_unidad"),
                "carga":                (float(t.precio_carga),      "fijo"),
                "descarga":             (float(t.precio_descarga),   "fijo"),
                "distribucion-interna": (float(t.precio_picking),    "por_unidad"),
                "distribucion-externa": (float(t.precio_picking),    "por_unidad"),
            }
            if tipo_servicio in legacy:
                p, tc_ = legacy[tipo_servicio]
                return {"precio": p, "tipo_calculo": tc_, "fuente": "legacy"}

    return {"precio": 0.0, "tipo_calculo": "por_unidad", "fuente": "sin_tarifa"}


def calcular_coste(precio: float, tipo_calculo: str, cantidad: float) -> float:
    """Calcula el coste según el tipo de cálculo.
    - fijo:       precio fijo independiente de cantidad (ej: carga/descarga)
    - por_mes:    precio fijo mensual (ej: alquiler espacio EMS GLOBE = 250€/mes)
    - por_dia:    precio × cantidad (ej: almacenaje NEW ERA = 0.17 × pallets × días)
    - por_unidad: precio × cantidad (ej: picking = 0.30 × unidades)
    """
    if tipo_calculo in ("fijo", "por_mes"):
        return round(precio, 2)
    elif tipo_calculo in ("por_dia", "por_unidad"):
        return round(precio * cantidad, 2)
    return 0.0

# ─────────────────────────────────────────────
# CLIENTES
# ─────────────────────────────────────────────

def get_all_clientes(db: Session) -> List[Cliente]:
    return db.query(Cliente).order_by(Cliente.empresa, Cliente.nombre).all()

def get_cliente_by_id(db: Session, cliente_id: int) -> Optional[Cliente]:
    return db.query(Cliente).filter(Cliente.id == cliente_id).first()

def create_cliente(db: Session, data: dict) -> Cliente:
    c = Cliente(**data)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

def update_cliente(db: Session, cliente_id: int, data: dict) -> Optional[Cliente]:
    c = get_cliente_by_id(db, cliente_id)
    if not c:
        return None
    for k, v in data.items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c

def delete_cliente(db: Session, cliente_id: int) -> bool:
    c = get_cliente_by_id(db, cliente_id)
    if not c:
        return False
    db.delete(c)
    db.commit()
    return True

# ─────────────────────────────────────────────
# STOCK
# ─────────────────────────────────────────────

def get_stock_activo(db: Session, cliente_id: Optional[int] = None) -> List[Stock]:
    q = db.query(Stock).filter(Stock.activo == True)
    if cliente_id:
        q = q.filter(Stock.cliente_id == cliente_id)
    return q.order_by(Stock.fecha_entrada.desc()).all()

def create_stock(db: Session, data: dict) -> Stock:
    s = Stock(**data)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

def dar_salida_pallet(db: Session, stock_id: int, fecha_salida: date) -> Optional[Stock]:
    s = db.query(Stock).filter(Stock.id == stock_id).first()
    if not s:
        return None
    s.fecha_salida = fecha_salida
    s.activo = False
    db.commit()
    db.refresh(s)
    return s

def delete_stock(db: Session, stock_id: int) -> bool:
    s = db.query(Stock).filter(Stock.id == stock_id).first()
    if not s:
        return False
    db.delete(s)
    db.commit()
    return True

# ─────────────────────────────────────────────
# MOVIMIENTOS
# ─────────────────────────────────────────────

def get_all_movimientos(db: Session, cliente_id: Optional[int] = None,
                         tipo: Optional[str] = None,
                         fecha_desde: Optional[date] = None,
                         fecha_hasta: Optional[date] = None) -> List[Movimiento]:
    q = db.query(Movimiento)
    if cliente_id:
        q = q.filter(Movimiento.cliente_id == cliente_id)
    if tipo:
        q = q.filter(Movimiento.tipo == tipo)
    if fecha_desde:
        q = q.filter(Movimiento.fecha >= fecha_desde)
    if fecha_hasta:
        q = q.filter(Movimiento.fecha <= fecha_hasta)
    return q.order_by(Movimiento.fecha.desc()).all()

def create_movimiento(db: Session, data: dict) -> Movimiento:
    """Crea movimiento calculando el coste automáticamente con el nuevo sistema."""
    cliente_id   = data["cliente_id"]
    tipo_servicio = data.get("tipo", "")
    cantidad     = float(data.get("cantidad", 1))

    info_precio  = resolver_precio(db, cliente_id, tipo_servicio)
    coste        = calcular_coste(info_precio["precio"], info_precio["tipo_calculo"], cantidad)
    data["coste"] = coste

    m = Movimiento(**data)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

def delete_movimiento(db: Session, mov_id: int) -> bool:
    m = db.query(Movimiento).filter(Movimiento.id == mov_id).first()
    if not m:
        return False
    db.delete(m)
    db.commit()
    return True

# ─────────────────────────────────────────────
# REPORTES
# ─────────────────────────────────────────────

def reporte_almacenaje(db: Session, mes: int, anio: int) -> List[Dict]:
    primer_dia = date(anio, mes, 1)
    ultimo_dia = date(anio, mes+1, 1) - timedelta(days=1) if mes < 12 else date(anio+1, 1, 1) - timedelta(days=1)

    stocks = (db.query(Stock)
              .filter(Stock.fecha_entrada <= ultimo_dia,
                      (Stock.fecha_salida >= primer_dia) | (Stock.fecha_salida == None))
              .all())
    rows = []
    for s in stocks:
        entrada_ef = max(s.fecha_entrada, primer_dia)
        salida_ef  = min(s.fecha_salida or ultimo_dia, ultimo_dia)
        dias       = max((salida_ef - entrada_ef).days + 1, 0)
        cliente    = get_cliente_by_id(db, s.cliente_id)
        info       = resolver_precio(db, s.cliente_id, "almacenaje")
        precio_dia = info["precio"]
        coste      = round(dias * precio_dia, 2)
        rows.append({
            "cliente": cliente.nombre if cliente else "—",
            "empresa": cliente.empresa if cliente else "—",
            "pallet": s.pallet, "referencia": s.referencia or "—",
            "fecha_entrada": s.fecha_entrada, "fecha_salida": s.fecha_salida,
            "dias": dias, "precio_dia": precio_dia, "coste": coste,
        })
    return rows

def reporte_operaciones(db: Session, mes: int, anio: int, tipo: Optional[str] = None) -> List[Dict]:
    primer_dia = date(anio, mes, 1)
    ultimo_dia = date(anio, mes+1, 1) - timedelta(days=1) if mes < 12 else date(anio+1, 1, 1) - timedelta(days=1)
    q = db.query(Movimiento).filter(Movimiento.fecha >= primer_dia, Movimiento.fecha <= ultimo_dia)
    if tipo:
        q = q.filter(Movimiento.tipo == tipo)
    rows = []
    for m in q.order_by(Movimiento.fecha.desc()).all():
        cliente = get_cliente_by_id(db, m.cliente_id)
        rows.append({
            "id": m.id, "cliente": cliente.nombre if cliente else "—",
            "empresa": cliente.empresa if cliente else "—",
            "tipo": m.tipo, "cantidad": float(m.cantidad),
            "fecha": m.fecha, "coste": float(m.coste or 0),
            "observaciones": m.observaciones or "",
        })
    return rows

def reporte_mensual_cliente(db: Session, mes: int, anio: int) -> List[Dict]:
    clientes = get_all_clientes(db)
    resumen  = []
    for c in clientes:
        alm_rows   = [r for r in reporte_almacenaje(db, mes, anio) if r["cliente"] == c.nombre]
        total_alm  = sum(r["coste"] for r in alm_rows)
        ops        = reporte_operaciones(db, mes, anio)
        ops_c      = [o for o in ops if o["cliente"] == c.nombre]
        pick_qty   = sum(o["cantidad"] for o in ops_c if o["tipo"] in ("picking","empaquetado","packing"))
        pick_cost  = sum(o["coste"]    for o in ops_c if o["tipo"] in ("picking","empaquetado","packing"))
        carga_qty  = sum(o["cantidad"] for o in ops_c if o["tipo"] == "carga")
        carga_cost = sum(o["coste"]    for o in ops_c if o["tipo"] == "carga")
        desc_qty   = sum(o["cantidad"] for o in ops_c if o["tipo"] == "descarga")
        desc_cost  = sum(o["coste"]    for o in ops_c if o["tipo"] == "descarga")
        dist_qty   = sum(o["cantidad"] for o in ops_c if "distribucion" in o["tipo"])
        dist_cost  = sum(o["coste"]    for o in ops_c if "distribucion" in o["tipo"])
        total      = total_alm + pick_cost + carga_cost + desc_cost + dist_cost
        if total > 0 or len(alm_rows) > 0:
            resumen.append({
                "cliente_id": c.id, "cliente": c.nombre,
                "empresa": c.empresa or "—",
                "condiciones_pago": c.condiciones_pago or "—",
                "tarifa": c.tarifa.nombre if c.tarifa else "Sin tarifa",
                "pallets_almacenados": len(alm_rows),
                "total_almacenaje": round(total_alm, 2),
                "picking_qty": int(pick_qty),   "picking_coste": round(pick_cost, 2),
                "cargas_qty": int(carga_qty),   "cargas_coste": round(carga_cost, 2),
                "descargas_qty": int(desc_qty), "descargas_coste": round(desc_cost, 2),
                "distribucion_qty": int(dist_qty), "distribucion_coste": round(dist_cost, 2),
                "total": round(total, 2),
            })
    return sorted(resumen, key=lambda x: x["total"], reverse=True)

def get_kpis_dashboard(db: Session) -> Dict:
    hoy           = date.today()
    primer_dia    = date(hoy.year, hoy.month, 1)
    total_clientes = db.query(func.count(Cliente.id)).scalar() or 0
    pallets_activos = db.query(func.count(Stock.id)).filter(Stock.activo == True).scalar() or 0
    movs_mes      = (db.query(func.count(Movimiento.id), func.sum(Movimiento.coste))
                     .filter(Movimiento.fecha >= primer_dia).first())
    ops_mes       = movs_mes[0] or 0
    facturacion_mes = float(movs_mes[1] or 0)
    total_facturado = float(db.query(func.sum(Movimiento.coste)).scalar() or 0)
    return {
        "total_clientes": total_clientes, "pallets_activos": pallets_activos,
        "ops_mes": ops_mes, "facturacion_mes": round(facturacion_mes, 2),
        "total_facturado": round(total_facturado, 2),
    }
