"""Solicitud de Endoso."""
from __future__ import annotations
import io
from datetime import date
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from core.pdf_builder import (
    draw_branded_page, get_styles, draw_text_block, draw_separator,
    draw_field_pair, MARGIN_LEFT, CONTENT_TOP, CONTENT_W, CONTENT_BOT,
    C_PURPLE, C_GOLD, PAGE_W, PAGE_H,
)
from core.document_types.base import BaseDocument


class SolicitudEndoso(BaseDocument):
    nombre      = "Solicitud de Endoso"
    descripcion = "Autorización para aplicar una póliza al cubrimiento de un crédito bancario."
    icono       = "📋"

    @classmethod
    def get_fields(cls) -> list[dict]:
        return [
            {"key": "banco",         "label": "Entidad bancaria (destinatario)", "type": "text",
             "required": True,  "placeholder": "Ej: AV VILLAS", "default": ""},
            {"key": "ciudad",        "label": "Ciudad",  "type": "text",
             "required": True,  "placeholder": "Ej: Medellín", "default": "Medellín"},
            {"key": "nombre_cliente","label": "Nombre completo del cliente", "type": "text",
             "required": True,  "placeholder": "Ej: JULIAN ARENAS BERRIO", "default": ""},
            {"key": "cedula",        "label": "Número de cédula", "type": "text",
             "required": True,  "placeholder": "Ej: 1036647333", "default": ""},
            {"key": "asesor",        "label": "Nombre del asesor PRADNA", "type": "text",
             "required": True,  "placeholder": "Ej: Yohanna Catalina Henao Herrera", "default": ""},
            {"key": "num_poliza",    "label": "Número de póliza", "type": "text",
             "required": True,  "placeholder": "Ej: 081005254338", "default": ""},
            {"key": "num_credito",   "label": "Número de crédito", "type": "text",
             "required": True,  "placeholder": "Ej: 33435680", "default": ""},
            {"key": "fecha",         "label": "Fecha del documento", "type": "date",
             "required": True,  "default": str(date.today())},
        ]

    @classmethod
    def build_pdf(cls, data: dict, numero: str) -> bytes:
        from reportlab.pdfgen import canvas as rl_canvas
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
        draw_branded_page(c, numero)
        S = get_styles()

        y = CONTENT_TOP

        # Título
        y = draw_text_block(c, "Solicitud Endoso", S["titulo"], MARGIN_LEFT, y, CONTENT_W)

        # Fecha
        try:
            from datetime import datetime
            dt = datetime.strptime(data.get("fecha", str(date.today())), "%Y-%m-%d")
            fecha_str = dt.strftime("%d de %B de %Y").capitalize()
        except Exception:
            fecha_str = data.get("fecha", str(date.today()))

        y = draw_text_block(c, fecha_str, S["fecha"], MARGIN_LEFT, y, CONTENT_W)
        y = draw_separator(c, y)
        y -= 4*mm

        # Destinatario
        y = draw_text_block(c, "Señores", S["normal"], MARGIN_LEFT, y, CONTENT_W)
        y = draw_text_block(c, f"<b>{data.get('banco','')}</b>", S["normal"], MARGIN_LEFT, y, CONTENT_W)
        y = draw_text_block(c, data.get("ciudad",""), S["normal"], MARGIN_LEFT, y, CONTENT_W)
        y -= 4*mm

        # Cuerpo
        nombre  = data.get("nombre_cliente", "")
        cedula  = data.get("cedula", "")
        asesor  = data.get("asesor", "")
        poliza  = data.get("num_poliza", "")
        credito = data.get("num_credito", "")

        cuerpo = (
            f"Yo <b>{nombre}</b> identificado con cédula <b>{cedula}</b> "
            f"autorizo a {asesor}, quien pertenece a <b>PRADNA Seguros</b>, para que "
            f"aplique la póliza número <b>{poliza}</b> al cubrimiento del crédito° <b>{credito}</b>."
        )
        y = draw_text_block(c, cuerpo, S["cuerpo"], MARGIN_LEFT, y, CONTENT_W)
        y -= 2*mm
        y = draw_text_block(c, "Muchas gracias por su pronta gestión.", S["cuerpo"], MARGIN_LEFT, y, CONTENT_W)
        y -= 8*mm
        y = draw_text_block(c, "Atentamente,", S["normal"], MARGIN_LEFT, y, CONTENT_W)

        # Firma
        firma_y = CONTENT_BOT + 32*mm
        cx = PAGE_W / 2
        # Línea de firma
        c.setStrokeColor(C_PURPLE)
        c.setLineWidth(1)
        c.line(cx - 35*mm, firma_y, cx + 35*mm, firma_y)

        para_n = Paragraph(f"<b>{nombre.upper()}</b>", S["firma_nombre"])
        para_c = Paragraph(cedula, S["firma_detalle"])
        w1, h1 = para_n.wrap(70*mm, 999)
        w2, h2 = para_c.wrap(70*mm, 999)
        para_n.drawOn(c, cx - 35*mm, firma_y - h1 - 2*mm)
        para_c.drawOn(c, cx - 35*mm, firma_y - h1 - h2 - 4*mm)

        c.save()
        buf.seek(0)
        return buf.getvalue()
