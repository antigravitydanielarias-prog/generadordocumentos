"""Solicitud de Endoso — Diseño Marca de Agua."""
from __future__ import annotations
import io
from datetime import date
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Paragraph
from core.pdf_builder import (
    draw_branded_page, get_styles, draw_text_block, draw_separator,
    draw_firma, MARGIN_L, MARGIN_R, CONTENT_W, CONTENT_TOP, CONTENT_BOT,
    C_PURPLE, C_GOLD, PAGE_W, PAGE_H, format_value,
    FIRMANTE_NOMBRE, FIRMANTE_CEDULA, FIRMANTE_CARGO,
)
from core.document_types.base import BaseDocument


class SolicitudEndoso(BaseDocument):
    nombre      = "Solicitud de Endoso"
    descripcion = "Autorización para aplicar una póliza al cubrimiento de un crédito bancario."
    icono       = "📋"

    @classmethod
    def get_fields(cls) -> list[dict]:
        return [
            {"key":"banco",          "label":"Entidad bancaria (destinatario)", "type":"text",
             "required":True, "placeholder":"AV VILLAS", "default":""},
            {"key":"ciudad",         "label":"Ciudad", "type":"text",
             "required":True, "placeholder":"Medellín", "default":"Medellín"},
            {"key":"nombre_cliente", "label":"Nombre completo del cliente", "type":"text",
             "required":True, "placeholder":"JULIAN ARENAS BERRIO", "default":""},
            {"key":"cedula",         "label":"Cédula del cliente", "type":"text",
             "required":True, "placeholder":"1036647333", "default":""},
            {"key":"num_poliza",     "label":"Número de póliza", "type":"text",
             "required":True, "placeholder":"081005254338", "default":""},
            {"key":"num_credito",    "label":"Número de crédito", "type":"text",
             "required":True, "placeholder":"33435680", "default":""},
            {"key":"fecha",          "label":"Fecha del documento", "type":"date",
             "required":True, "default":str(date.today())},
        ]

    @classmethod
    def build_pdf(cls, data: dict, numero: str) -> bytes:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
        draw_branded_page(c, numero)
        S = get_styles()
        y = CONTENT_TOP

        # Título
        y = draw_text_block(c, "Solicitud de Endoso", S["titulo"], MARGIN_L, y, CONTENT_W)

        # Fecha
        try:
            from datetime import datetime
            dt = datetime.strptime(data.get("fecha", str(date.today())), "%Y-%m-%d")
            fecha_str = f"{data.get('ciudad','Medellín')}, {dt.strftime('%d de %B de %Y').capitalize()}"
        except Exception:
            fecha_str = f"{data.get('ciudad','Medellín')}, {data.get('fecha','')}"

        y = draw_text_block(c, fecha_str, S["fecha"], MARGIN_L, y, CONTENT_W)
        y = draw_separator(c, y)
        y -= 4*mm

        # Destinatario
        y = draw_text_block(c, "Señores", S["normal"], MARGIN_L, y, CONTENT_W)
        y = draw_text_block(c, f"<b>{data.get('banco','')}</b>", S["normal"], MARGIN_L, y, CONTENT_W)
        y = draw_text_block(c, data.get("ciudad",""), S["normal"], MARGIN_L, y, CONTENT_W)
        y -= 4*mm

        # Cuerpo
        nombre  = data.get("nombre_cliente","")
        cedula  = data.get("cedula","")
        poliza  = data.get("num_poliza","")
        credito = data.get("num_credito","")
        cuerpo = (
            f"Yo <b>{nombre}</b> identificado(a) con cédula <b>{cedula}</b>, "
            f"autorizo a {FIRMANTE_NOMBRE}, quien pertenece a <b>PRADNA Seguros</b>, para que "
            f"aplique la póliza número <b>{poliza}</b> al cubrimiento del crédito° <b>{credito}</b>."
        )
        y = draw_text_block(c, cuerpo, S["cuerpo"], MARGIN_L, y, CONTENT_W)
        y -= 2*mm
        y = draw_text_block(c, "Muchas gracias por su pronta gestión.", S["normal"], MARGIN_L, y, CONTENT_W)
        y -= 8*mm
        y = draw_text_block(c, "Atentamente,", S["normal"], MARGIN_L, y, CONTENT_W)

        # Firma
        firma_y = CONTENT_BOT + 38*mm
        draw_firma(c, firma_y)

        # Firma cliente debajo del texto "Atentamente"
        cliente_y = y - 18*mm
        cx = PAGE_W / 4
        c.setStrokeColor(C_PURPLE)
        c.setLineWidth(0.75)
        c.line(cx - 30*mm, cliente_y, cx + 30*mm, cliente_y)
        p1 = Paragraph(f"<b>{nombre.upper()}</b>", S["firma_nombre"])
        p2 = Paragraph(f"C.C. {cedula}", S["firma_detalle"])
        w,h1 = p1.wrap(60*mm,999); w,h2 = p2.wrap(60*mm,999)
        p1.drawOn(c, cx-30*mm, cliente_y-h1-2*mm)
        p2.drawOn(c, cx-30*mm, cliente_y-h1-h2-4*mm)

        c.save(); buf.seek(0)
        return buf.getvalue()
