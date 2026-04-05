"""Comunicado / Carta — Diseño Marca de Agua."""
from __future__ import annotations
import io
from datetime import date
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from core.pdf_builder import (
    draw_branded_page, get_styles, draw_text_block, draw_separator,
    draw_firma, MARGIN_L, CONTENT_W, CONTENT_TOP, CONTENT_BOT,
    C_PURPLE, PAGE_W, PAGE_H, FIRMANTE_NOMBRE,
)
from core.document_types.base import BaseDocument


class Comunicado(BaseDocument):
    nombre      = "Comunicado / Carta"
    descripcion = "Carta formal o comunicado institucional con membrete PRADNA."
    icono       = "✉️"

    @classmethod
    def get_fields(cls) -> list[dict]:
        return [
            {"key":"ciudad",       "label":"Ciudad", "type":"text",
             "required":True, "placeholder":"Medellín", "default":"Medellín"},
            {"key":"fecha",        "label":"Fecha", "type":"date",
             "required":True, "default":str(date.today())},
            {"key":"destinatario", "label":"Destinatario", "type":"text",
             "required":True, "placeholder":"Dr. Carlos Ramírez", "default":""},
            {"key":"cargo_dest",   "label":"Cargo / empresa", "type":"text",
             "required":False, "placeholder":"Gerente · Banco AV Villas", "default":""},
            {"key":"asunto",       "label":"Asunto", "type":"text",
             "required":True, "placeholder":"Aplicación de póliza a crédito hipotecario", "default":""},
            {"key":"saludo",       "label":"Saludo", "type":"text",
             "required":True, "placeholder":"Estimados señores:", "default":"Estimados señores:"},
            {"key":"cuerpo",       "label":"Cuerpo del comunicado", "type":"textarea",
             "required":True, "placeholder":"Redacta el contenido...", "default":""},
            {"key":"cierre",       "label":"Frase de cierre", "type":"text",
             "required":True, "default":"Quedamos atentos a cualquier inquietud."},
        ]

    @classmethod
    def build_pdf(cls, data: dict, numero: str) -> bytes:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
        draw_branded_page(c, numero)
        S = get_styles()
        y = CONTENT_TOP

        y = draw_text_block(c, data.get("asunto","Comunicado"), S["titulo"], MARGIN_L, y, CONTENT_W)

        try:
            from datetime import datetime
            dt = datetime.strptime(data.get("fecha", str(date.today())), "%Y-%m-%d")
            fecha_str = f"{data.get('ciudad','Medellín')}, {dt.strftime('%d de %B de %Y').capitalize()}"
        except Exception:
            fecha_str = f"{data.get('ciudad','')}, {data.get('fecha','')}"

        y = draw_text_block(c, fecha_str, S["fecha"], MARGIN_L, y, CONTENT_W)
        y = draw_separator(c, y)
        y -= 5*mm

        dest    = data.get("destinatario","")
        cargo_d = data.get("cargo_dest","")
        y = draw_text_block(c, f"<b>{dest}</b>", S["normal"], MARGIN_L, y, CONTENT_W)
        if cargo_d:
            y = draw_text_block(c, cargo_d, S["normal"], MARGIN_L, y, CONTENT_W)
        y -= 4*mm

        y = draw_text_block(c, data.get("saludo",""), S["normal"], MARGIN_L, y, CONTENT_W)
        y -= 3*mm

        cuerpo = data.get("cuerpo","").replace("\n","<br/>")
        y = draw_text_block(c, cuerpo, S["cuerpo"], MARGIN_L, y, CONTENT_W)
        y -= 4*mm
        y = draw_text_block(c, data.get("cierre",""), S["cuerpo"], MARGIN_L, y, CONTENT_W)
        y -= 6*mm
        draw_text_block(c, "Atentamente,", S["normal"], MARGIN_L, y, CONTENT_W)

        draw_firma(c, CONTENT_BOT + 38*mm)
        c.save(); buf.seek(0)
        return buf.getvalue()
