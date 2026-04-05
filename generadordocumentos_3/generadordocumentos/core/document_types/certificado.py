"""Certificado / Constancia — Diseño Marca de Agua."""
from __future__ import annotations
import io
from datetime import date
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Paragraph
from core.pdf_builder import (
    draw_branded_page, get_styles, draw_text_block, draw_separator,
    draw_firma, MARGIN_L, CONTENT_W, CONTENT_TOP, CONTENT_BOT,
    C_PURPLE, C_GOLD, PAGE_W, PAGE_H,
    FIRMANTE_NOMBRE, FIRMANTE_CEDULA, FIRMANTE_CARGO,
)
from core.document_types.base import BaseDocument


class Certificado(BaseDocument):
    nombre      = "Certificado / Constancia"
    descripcion = "Certifica hechos, coberturas o situaciones para uso oficial."
    icono       = "🏅"

    @classmethod
    def get_fields(cls) -> list[dict]:
        return [
            {"key":"tipo_cert",   "label":"Tipo de certificado", "type":"select",
             "options":["Certificado de Cobertura","Certificado de Vinculación",
                        "Constancia de Pago","Constancia de Vigencia",
                        "Certificado de Beneficiario","Otro"],
             "required":True, "default":"Certificado de Cobertura"},
            {"key":"ciudad",      "label":"Ciudad", "type":"text",
             "required":True, "placeholder":"Medellín", "default":"Medellín"},
            {"key":"fecha",       "label":"Fecha", "type":"date",
             "required":True, "default":str(date.today())},
            {"key":"certifica_a", "label":"Nombre del titular", "type":"text",
             "required":True, "placeholder":"CAROLINA CANO PEREA", "default":""},
            {"key":"cedula",      "label":"Identificación", "type":"text",
             "required":True, "placeholder":"C.C. 1036647333", "default":""},
            {"key":"poliza",      "label":"Número de póliza (si aplica)", "type":"text",
             "required":False, "placeholder":"081005254338", "default":""},
            {"key":"contenido",   "label":"Contenido del certificado", "type":"textarea",
             "required":True, "placeholder":"Redacta el contenido...", "default":""},
        ]

    @classmethod
    def build_pdf(cls, data: dict, numero: str) -> bytes:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
        draw_branded_page(c, numero)
        S = get_styles()
        y = CONTENT_TOP

        tipo = data.get("tipo_cert","Certificado")
        y = draw_text_block(c, tipo, S["titulo"], MARGIN_L, y, CONTENT_W)

        try:
            from datetime import datetime
            dt = datetime.strptime(data.get("fecha", str(date.today())), "%Y-%m-%d")
            fecha_str = f"{data.get('ciudad','Medellín')}, {dt.strftime('%d de %B de %Y').capitalize()}"
        except Exception:
            fecha_str = f"{data.get('ciudad','')}, {data.get('fecha','')}"

        y = draw_text_block(c, fecha_str, S["fecha"], MARGIN_L, y, CONTENT_W)
        y = draw_separator(c, y)
        y -= 5*mm

        y = draw_text_block(c, "PRADNA SEGUROS CERTIFICA QUE:", S["subtitulo"], MARGIN_L, y, CONTENT_W)
        y -= 2*mm

        nombre = data.get("certifica_a","")
        cedula = data.get("cedula","")
        poliza = data.get("poliza","")

        intro = f"<b>{nombre}</b>, identificado(a) con {cedula}"
        if poliza:
            intro += f", titular de la póliza número <b>{poliza}</b>"
        intro += ","
        y = draw_text_block(c, intro, S["cuerpo"], MARGIN_L, y, CONTENT_W)

        contenido = data.get("contenido","").replace("\n","<br/>")
        y = draw_text_block(c, contenido, S["cuerpo"], MARGIN_L, y, CONTENT_W)
        y -= 4*mm
        y = draw_text_block(c,
            "El presente certificado se expide a solicitud del interesado para los fines que estime convenientes.",
            S["cuerpo"], MARGIN_L, y, CONTENT_W)

        draw_firma(c, CONTENT_BOT + 38*mm)
        c.save(); buf.seek(0)
        return buf.getvalue()
