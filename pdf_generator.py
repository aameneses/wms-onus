"""
pdf_generator.py - Generación de PDFs para WMS con ReportLab
"""
import io
from datetime import date
from typing import List, Dict, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
from reportlab.platypus import Image as RLImage
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo_white.png")


# ─────────────────────────────────────────────
# COLORES ONUS EXPRESS
# ─────────────────────────────────────────────
AZUL_DARK   = colors.HexColor("#000935")   # Azul corporativo ONUS
AZUL_MED    = colors.HexColor("#001a6e")   # Azul medio
AZUL_LIGHT  = colors.HexColor("#00C9CE")   # Turquesa ONUS
GRIS_LIGHT  = colors.HexColor("#f1f5f9")
GRIS_MED    = colors.HexColor("#cbd5e1")
BLANCO      = colors.white
VERDE       = colors.HexColor("#16a34a")
ROJO        = colors.HexColor("#dc2626")
NARANJA     = colors.HexColor("#00C9CE")   # Turquesa en lugar de naranja


def _estilos():
    styles = getSampleStyleSheet()
    extra = {
        "titulo_doc": ParagraphStyle(
            "titulo_doc", parent=styles["Title"],
            fontSize=22, textColor=BLANCO, spaceAfter=4,
            fontName="Helvetica-Bold", alignment=TA_CENTER,
        ),
        "subtitulo_doc": ParagraphStyle(
            "subtitulo_doc", parent=styles["Normal"],
            fontSize=11, textColor=GRIS_MED, spaceAfter=6,
            fontName="Helvetica", alignment=TA_CENTER,
        ),
        "seccion": ParagraphStyle(
            "seccion", parent=styles["Heading2"],
            fontSize=13, textColor=AZUL_DARK, spaceBefore=14,
            spaceAfter=6, fontName="Helvetica-Bold",
        ),
        "normal": ParagraphStyle(
            "normal", parent=styles["Normal"],
            fontSize=9, textColor=AZUL_DARK, fontName="Helvetica",
        ),
        "negrita": ParagraphStyle(
            "negrita", parent=styles["Normal"],
            fontSize=9, textColor=AZUL_DARK, fontName="Helvetica-Bold",
        ),
        "total": ParagraphStyle(
            "total", parent=styles["Normal"],
            fontSize=11, textColor=AZUL_MED,
            fontName="Helvetica-Bold", alignment=TA_RIGHT,
        ),
        "footer": ParagraphStyle(
            "footer", parent=styles["Normal"],
            fontSize=8, textColor=GRIS_MED,
            fontName="Helvetica", alignment=TA_CENTER,
        ),
    }
    return extra


def _tabla_style_base():
    return [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_MED),
        ("TEXTCOLOR",  (0, 0), (-1, 0), BLANCO),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 9),
        ("ALIGN",      (0, 0), (-1, 0), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANCO, GRIS_LIGHT]),
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",   (0, 1), (-1, -1), 8),
        ("ALIGN",      (0, 1), (-1, -1), "LEFT"),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",       (0, 0), (-1, -1), 0.3, GRIS_MED),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]


def _cabecera(story, titulo: str, subtitulo: str, estilos: dict):
    """Genera cabecera con fondo ONUS EXPRESS y logo."""
    ancho = A4[0] - 4 * cm
    # Logo en cabecera
    if os.path.exists(LOGO_PATH):
        logo = RLImage(LOGO_PATH, width=4*cm, height=1.4*cm)
        logo_cell = logo
    else:
        logo_cell = Paragraph("<b>ONUS EXPRESS</b>", estilos["subtitulo_doc"])

    # Turquesa accent bar
    accent = Table([[""]], colWidths=[ancho])
    accent.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), AZUL_LIGHT),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
    ]))

    data = [
        [logo_cell, Paragraph(titulo, estilos["titulo_doc"])],
        ["",         Paragraph(subtitulo, estilos["subtitulo_doc"])],
    ]
    col_w = [4.5*cm, ancho - 4.5*cm]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), AZUL_DARK),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (0, 0), (0, -1),  "LEFT"),
        ("ALIGN",         (1, 0), (1, -1),  "RIGHT"),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("SPAN",          (0, 0), (0, -1)),
    ]))
    story.append(t)
    story.append(accent)
    story.append(Spacer(1, 0.4 * cm))


# ─────────────────────────────────────────────
# PDF: INFORME DE ALMACENAJE
# ─────────────────────────────────────────────

def generar_pdf_almacenaje(rows: List[Dict], mes: int, anio: int) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm
    )
    estilos = _estilos()
    story = []

    MESES = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

    _cabecera(story,
              "📦 Informe de Almacenaje",
              f"{MESES[mes]} {anio}  ·  Generado el {date.today().strftime('%d/%m/%Y')}",
              estilos)

    story.append(Paragraph("Detalle de Pallets Almacenados", estilos["seccion"]))

    headers = ["Cliente", "Empresa", "Pallet", "Referencia",
               "F. Entrada", "F. Salida", "Días", "€/día", "Total €"]
    data = [headers]
    total_coste = 0.0
    for r in rows:
        fe = r["fecha_entrada"].strftime("%d/%m/%Y") if r["fecha_entrada"] else "—"
        fs = r["fecha_salida"].strftime("%d/%m/%Y") if r.get("fecha_salida") else "Activo"
        data.append([
            r["cliente"], r["empresa"], r["pallet"], r["referencia"],
            fe, fs, str(r["dias"]),
            f"{r['precio_dia']:.2f}", f"{r['coste']:.2f}"
        ])
        total_coste += r["coste"]

    anchos = [3*cm, 3.5*cm, 2.2*cm, 2.5*cm, 2*cm, 2*cm, 1.3*cm, 1.3*cm, 1.7*cm]
    t = Table(data, colWidths=anchos, repeatRows=1)
    st = _tabla_style_base()
    st += [
        ("ALIGN", (6, 1), (-1, -1), "RIGHT"),
        ("FONTNAME", (-1, 1), (-1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (-1, 1), (-1, -1), AZUL_MED),
    ]
    t.setStyle(TableStyle(st))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(f"Total Almacenaje: <b>{total_coste:.2f} €</b>", estilos["total"]))

    doc.build(story)
    return buf.getvalue()


# ─────────────────────────────────────────────
# PDF: INFORME DE OPERACIONES
# ─────────────────────────────────────────────

def generar_pdf_operaciones(rows: List[Dict], tipo: str, mes: int, anio: int) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm
    )
    estilos = _estilos()
    story = []
    MESES = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

    titulos_tipo = {
        "picking": "🔍 Informe de Picking",
        "packing": "📦 Informe de Packing",
        "carga":   "🚛 Informe de Cargas",
        "descarga":"🏭 Informe de Descargas",
    }
    titulo = titulos_tipo.get(tipo, f"Informe {tipo.title()}")
    _cabecera(story, titulo, f"{MESES[mes]} {anio}", estilos)

    story.append(Paragraph(f"Detalle de Operaciones · {tipo.title()}", estilos["seccion"]))

    headers = ["ID", "Cliente", "Empresa", "Tipo", "Cantidad", "Fecha", "Coste €", "Observaciones"]
    data = [headers]
    total_coste = 0.0
    total_qty = 0.0
    for r in rows:
        data.append([
            str(r["id"]), r["cliente"], r["empresa"],
            r["tipo"].title(), f"{r['cantidad']:.0f}",
            r["fecha"].strftime("%d/%m/%Y") if r["fecha"] else "—",
            f"{r['coste']:.2f}",
            r.get("observaciones","")[:40] or "—",
        ])
        total_coste += r["coste"]
        total_qty += r["cantidad"]

    anchos = [1*cm, 2.8*cm, 3*cm, 1.8*cm, 1.5*cm, 2*cm, 1.8*cm, 4.1*cm]
    t = Table(data, colWidths=anchos, repeatRows=1)
    st = _tabla_style_base()
    st += [("ALIGN", (4, 1), (6, -1), "RIGHT")]
    t.setStyle(TableStyle(st))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"Total operaciones: <b>{int(total_qty)}</b>  ·  "
        f"Total coste: <b>{total_coste:.2f} €</b>",
        estilos["total"]
    ))

    doc.build(story)
    return buf.getvalue()


# ─────────────────────────────────────────────
# PDF: RESUMEN MENSUAL POR CLIENTE (FACTURA)
# ─────────────────────────────────────────────

def generar_pdf_factura_cliente(resumen: Dict, mes: int, anio: int, detalle_almacenaje: List[Dict], detalle_ops: List[Dict]) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm
    )
    estilos = _estilos()
    story = []
    MESES = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

    _cabecera(story,
              "🧾 Resumen de Facturación",
              f"{resumen['cliente']} · {resumen['empresa']} · {MESES[mes]} {anio}",
              estilos)

    # Datos cliente
    story.append(Paragraph("Datos del Cliente", estilos["seccion"]))
    info = [
        ["Cliente:", resumen["cliente"], "Empresa:", resumen["empresa"]],
        ["Tarifa:", resumen["tarifa"], "Condiciones:", resumen["condiciones_pago"]],
    ]
    t_info = Table(info, colWidths=[3*cm, 5*cm, 3*cm, 5*cm])
    t_info.setStyle(TableStyle([
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("BACKGROUND", (0,0), (-1,-1), GRIS_LIGHT),
        ("GRID", (0,0), (-1,-1), 0.3, GRIS_MED),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 0.3*cm))

    # Resumen de conceptos
    story.append(Paragraph("Resumen de Servicios", estilos["seccion"]))
    conceptos = [
        ["Concepto", "Unidades", "Total €"],
        ["Almacenaje (pallets × días)", str(resumen["pallets_almacenados"]), f"{resumen['total_almacenaje']:.2f}"],
        [f"Picking / Packing",          str(resumen["picking_qty"]),         f"{resumen['picking_coste']:.2f}"],
        [f"Cargas",                     str(resumen["cargas_qty"]),           f"{resumen['cargas_coste']:.2f}"],
        [f"Descargas",                  str(resumen["descargas_qty"]),        f"{resumen['descargas_coste']:.2f}"],
    ]
    t_conc = Table(conceptos, colWidths=[9*cm, 3*cm, 4*cm])
    st = _tabla_style_base()
    st += [
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (-1, 1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
    ]
    t_conc.setStyle(TableStyle(st))
    story.append(t_conc)
    story.append(Spacer(1, 0.2*cm))

    # Total
    total_data = [["", "TOTAL A FACTURAR:", f"{resumen['total']:.2f} €"]]
    t_total = Table(total_data, colWidths=[9*cm, 3*cm, 4*cm])
    t_total.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), AZUL_DARK),
        ("TEXTCOLOR",  (0,0), (-1,-1), BLANCO),
        ("FONTNAME",   (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 12),
        ("ALIGN",      (1,0), (-1,-1), "RIGHT"),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
    ]))
    story.append(t_total)

    # Detalle almacenaje
    if detalle_almacenaje:
        story.append(Paragraph("Detalle: Pallets Almacenados", estilos["seccion"]))
        hdr = ["Pallet", "Referencia", "F. Entrada", "F. Salida", "Días", "€/día", "Total"]
        data = [hdr]
        for r in detalle_almacenaje:
            fs = r["fecha_salida"].strftime("%d/%m/%Y") if r.get("fecha_salida") else "Activo"
            data.append([
                r["pallet"], r["referencia"],
                r["fecha_entrada"].strftime("%d/%m/%Y"),
                fs, str(r["dias"]),
                f"{r['precio_dia']:.2f}", f"{r['coste']:.2f}"
            ])
        t_d = Table(data, colWidths=[2.5*cm,2.5*cm,2.3*cm,2.3*cm,1.2*cm,1.5*cm,1.7*cm])
        st2 = _tabla_style_base()
        st2 += [("ALIGN", (4,1), (-1,-1), "RIGHT")]
        t_d.setStyle(TableStyle(st2))
        story.append(t_d)

    # Detalle operaciones
    if detalle_ops:
        story.append(Paragraph("Detalle: Operaciones del Mes", estilos["seccion"]))
        hdr2 = ["Tipo", "Cantidad", "Fecha", "Coste €", "Observaciones"]
        data2 = [hdr2]
        for o in detalle_ops:
            data2.append([
                o["tipo"].title(), f"{o['cantidad']:.0f}",
                o["fecha"].strftime("%d/%m/%Y") if o["fecha"] else "—",
                f"{o['coste']:.2f}",
                (o.get("observaciones","") or "—")[:50],
            ])
        t_d2 = Table(data2, colWidths=[2.5*cm,1.8*cm,2.2*cm,2*cm,7.5*cm])
        t_d2.setStyle(TableStyle(_tabla_style_base()))
        story.append(t_d2)

    # Footer
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS_MED))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Documento generado automáticamente · WMS ONUS EXPRESS · {date.today().strftime('%d/%m/%Y')}",
        estilos["footer"]
    ))

    doc.build(story)
    return buf.getvalue()


# ─────────────────────────────────────────────
# PDF: INFORME MENSUAL GLOBAL
# ─────────────────────────────────────────────

def generar_pdf_resumen_mensual(resumen_list: List[Dict], mes: int, anio: int) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm
    )
    estilos = _estilos()
    story = []
    MESES = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

    _cabecera(story, "📊 Informe Mensual Global", f"{MESES[mes]} {anio}", estilos)

    story.append(Paragraph("Resumen por Cliente", estilos["seccion"]))

    headers = ["Cliente", "Empresa", "Tarifa", "Almacenaje €",
               "Picking €", "Cargas €", "Descargas €", "TOTAL €"]
    data = [headers]
    grand_total = 0.0
    for r in resumen_list:
        data.append([
            r["cliente"], r["empresa"], r["tarifa"],
            f"{r['total_almacenaje']:.2f}",
            f"{r['picking_coste']:.2f}",
            f"{r['cargas_coste']:.2f}",
            f"{r['descargas_coste']:.2f}",
            f"{r['total']:.2f}",
        ])
        grand_total += r["total"]

    data.append(["", "", "TOTAL GLOBAL", "", "", "", "", f"{grand_total:.2f}"])

    anchos = [3*cm, 3.5*cm, 2.5*cm, 2*cm, 1.8*cm, 1.8*cm, 1.9*cm, 1.5*cm]
    t = Table(data, colWidths=anchos, repeatRows=1)
    st = _tabla_style_base()
    st += [
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
        ("FONTNAME", (-1, 1), (-1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (-1, 1), (-1, -1), AZUL_MED),
        ("BACKGROUND", (0, -1), (-1, -1), AZUL_DARK),
        ("TEXTCOLOR",  (0, -1), (-1, -1), BLANCO),
        ("FONTNAME",   (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",   (0, -1), (-1, -1), 10),
    ]
    t.setStyle(TableStyle(st))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Facturación total del mes: <b>{grand_total:.2f} €</b>", estilos["total"]))

    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS_MED))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Generado automáticamente · WMS ONUS EXPRESS · {date.today().strftime('%d/%m/%Y')}",
        estilos["footer"]
    ))

    doc.build(story)
    return buf.getvalue()
