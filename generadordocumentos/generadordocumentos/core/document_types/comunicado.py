"""Comunicado interno / Carta."""
from __future__ import annotations
import io
from datetime import date
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Paragraph
from core.pdf_builder import (
    draw_branded_page, get_styles, draw_text_block, draw_separator,
    MARGIN_LEFT, CONTENT_TOP, CONTENT_W, CONTENT_BOT,
    C_PURPLE, C_GOLD, PAGE_W, PAGE_H,
)
from core.document_types.base import BaseDocument


class Comunicado(BaseDocument):
    nombre      = "Comunicado / Carta"
    descripcion = "Carta formal o comunicado institucional con membrete PRADNA."
    icono       = "✉️"

    @classmethod
    def get_fields(cls) -> list[dict]:
        return [
            {"key": "ciudad",       "label": "Ciudad", "type": "text",
             "required": True, "placeholder": "Medellín", "default": "Medellín"},
            {"key": "fecha",        "label": "Fecha", "type": "date",
             "required": True, "default": str(date.today())},
            {"key": "destinatario", "label": "Destinatario (nombre)", "type": "text",
             "required": True, "placeholder": "Nombre del destinatario", "default": ""},
            {"key": "cargo_dest",   "label": "Cargo / empresa del destinatario", "type": "text",
             "required": False, "placeholder": "Ej: Gerente de Riesgo · Bancolombia", "default": ""},
            {"key": "asunto",       "label": "Asunto", "type": "text",
             "required": True, "placeholder": "Asunto del comunicado", "default": ""},
            {"key": "saludo",       "label": "Saludo", "type": "text",
             "required": True, "placeholder": "Ej: Estimado señor García:", "default": "Estimados señores:"},
            {"key": "cuerpo",       "label": "Cuerpo del comunicado", "type": "textarea",
             "required": True, "placeholder": "Redacta el contenido del comunicado...", "default": ""},
            {"key": "cierre",       "label": "Frase de cierre", "type": "text",
             "required": True, "placeholder": "Ej: Quedamos atentos a cualquier inquietud.",
             "default": "Quedamos atentos a cualquier inquietud que pueda surgir."},
            {"key": "firmante",     "label": "Nombre del firmante", "type": "text",
             "required": True, "placeholder": "Tu nombre completo", "default": ""},
            {"key": "cargo",        "label": "Cargo del firmante", "type": "text",
             "required": True, "placeholder": "Ej: Asesora Comercial", "default": ""},
        ]

    @classmethod
    def build_pdf(cls, data: dict, numero: str) -> bytes:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
        draw_branded_page(c, numero)
        S = get_styles()

        y = CONTENT_TOP

        # Asunto como título
        asunto = data.get("asunto", "Comunicado")
        y = draw_text_block(c, asunto, S["titulo"], MARGIN_LEFT, y, CONTENT_W)

        # Ciudad y fecha
        try:
            from datetime import datetime
            dt = datetime.strptime(data.get("fecha", str(date.today())), "%Y-%m-%d")
            fecha_str = f"{data.get('ciudad','Medellín')}, {dt.strftime('%d de %B de %Y').capitalize()}"
        except Exception:
            fecha_str = f"{data.get('ciudad','')}, {data.get('fecha','')}"

        y = draw_text_block(c, fecha_str, S["fecha"], MARGIN_LEFT, y, CONTENT_W)
        y = draw_separator(c, y)
        y -= 5*mm

        # Destinatario
        dest  = data.get("destinatario","")
        cargo_d = data.get("cargo_dest","")
        y = draw_text_block(c, f"<b>{dest}</b>", S["normal"], MARGIN_LEFT, y, CONTENT_W)
        if cargo_d:
            y = draw_text_block(c, cargo_d, S["normal"], MARGIN_LEFT, y, CONTENT_W)
        y -= 4*mm

        # Saludo
        saludo = data.get("saludo","Estimados señores:")
        y = draw_text_block(c, saludo, S["normal"], MARGIN_LEFT, y, CONTENT_W)
        y -= 3*mm

        # Cuerpo — puede tener saltos de línea
        cuerpo = data.get("cuerpo","").replace("\n","<br/>")
        y = draw_text_block(c, cuerpo, S["cuerpo"], MARGIN_LEFT, y, CONTENT_W)
        y -= 4*mm

        # Cierre
        cierre = data.get("cierre","")
        y = draw_text_block(c, cierre, S["cuerpo"], MARGIN_LEFT, y, CONTENT_W)
        y -= 6*mm
        y = draw_text_block(c, "Atentamente,", S["normal"], MARGIN_LEFT, y, CONTENT_W)

        # Firma
        firma_y = CONTENT_BOT + 36*mm
        cx = PAGE_W / 2
        c.setStrokeColor(C_PURPLE)
        c.setLineWidth(1)
        c.line(cx - 40*mm, firma_y, cx + 40*mm, firma_y)

        firmante = data.get("firmante","")
        cargo    = data.get("cargo","")
        p1 = Paragraph(f"<b>{firmante.upper()}</b>", S["firma_nombre"])
        p2 = Paragraph(cargo, S["firma_detalle"])
        p3 = Paragraph("PRADNA Seguros · Protección que transciende", S["firma_detalle"])
        w1,h1 = p1.wrap(80*mm,999)
        w2,h2 = p2.wrap(80*mm,999)
        w3,h3 = p3.wrap(80*mm,999)
        p1.drawOn(c, cx-40*mm, firma_y-h1-2*mm)
        p2.drawOn(c, cx-40*mm, firma_y-h1-h2-4*mm)
        p3.drawOn(c, cx-40*mm, firma_y-h1-h2-h3-7*mm)

        c.save()
        buf.seek(0)
        return buf.getvalue()
