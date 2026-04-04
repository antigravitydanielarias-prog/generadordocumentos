"""Certificado / Constancia."""
from __future__ import annotations
import io
from datetime import date
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Paragraph
from core.pdf_builder import (
    draw_branded_page, get_styles, draw_text_block, draw_separator,
    MARGIN_LEFT, CONTENT_TOP, CONTENT_W, CONTENT_BOT,
    C_PURPLE, C_GOLD, C_PURPLE_MID, PAGE_W, PAGE_H,
)
from core.document_types.base import BaseDocument


class Certificado(BaseDocument):
    nombre      = "Certificado / Constancia"
    descripcion = "Certifica hechos, coberturas, calidades o situaciones para uso oficial."
    icono       = "🏅"

    @classmethod
    def get_fields(cls) -> list[dict]:
        return [
            {"key": "tipo_cert",    "label": "Tipo de certificado", "type": "select",
             "options": ["Certificado de Cobertura","Certificado de Vinculación",
                         "Constancia de Pago","Constancia de Vigencia",
                         "Certificado de Beneficiario","Otro"],
             "required": True, "default": "Certificado de Cobertura"},
            {"key": "ciudad",       "label": "Ciudad y fecha", "type": "text",
             "required": True, "placeholder": "Medellín", "default": "Medellín"},
            {"key": "fecha",        "label": "Fecha",  "type": "date",
             "required": True, "default": str(date.today())},
            {"key": "certifica_a",  "label": "Se certifica / consta que", "type": "text",
             "required": True, "placeholder": "Nombre completo del titular", "default": ""},
            {"key": "cedula",       "label": "Identificación", "type": "text",
             "required": True, "placeholder": "C.C. 1036647333", "default": ""},
            {"key": "poliza",       "label": "Número de póliza (si aplica)", "type": "text",
             "required": False, "placeholder": "081005254338", "default": ""},
            {"key": "contenido",    "label": "Descripción / contenido del certificado",
             "type": "textarea", "required": True,
             "placeholder": "Redacta el contenido del certificado...", "default": ""},
            {"key": "firmante",     "label": "Nombre del firmante",  "type": "text",
             "required": True, "placeholder": "Yohanna Catalina Henao Herrera", "default": ""},
            {"key": "cargo",        "label": "Cargo del firmante", "type": "text",
             "required": True, "placeholder": "Asesora Comercial · PRADNA Seguros", "default": ""},
        ]

    @classmethod
    def build_pdf(cls, data: dict, numero: str) -> bytes:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
        draw_branded_page(c, numero)
        S = get_styles()

        y = CONTENT_TOP

        # Tipo de certificado como título
        tipo = data.get("tipo_cert", "Certificado")
        y = draw_text_block(c, tipo, S["titulo"], MARGIN_LEFT, y, CONTENT_W)

        # Ciudad y fecha
        try:
            from datetime import datetime
            dt = datetime.strptime(data.get("fecha", str(date.today())), "%Y-%m-%d")
            fecha_str = f"{data.get('ciudad', 'Medellín')}, {dt.strftime('%d de %B de %Y').capitalize()}"
        except Exception:
            fecha_str = f"{data.get('ciudad', '')}, {data.get('fecha', '')}"

        y = draw_text_block(c, fecha_str, S["fecha"], MARGIN_LEFT, y, CONTENT_W)
        y = draw_separator(c, y)
        y -= 6*mm

        # Encabezado formal
        y = draw_text_block(c, "PRADNA SEGUROS CERTIFICA QUE:", S["subtitulo"], MARGIN_LEFT, y, CONTENT_W)
        y -= 2*mm

        # Quién
        nombre  = data.get("certifica_a", "")
        cedula  = data.get("cedula", "")
        poliza  = data.get("poliza", "")

        intro = f"<b>{nombre}</b>, identificado(a) con {cedula}"
        if poliza:
            intro += f", titular de la póliza número <b>{poliza}</b>"
        intro += ","
        y = draw_text_block(c, intro, S["cuerpo"], MARGIN_LEFT, y, CONTENT_W)

        # Contenido
        contenido = data.get("contenido", "")
        y = draw_text_block(c, contenido, S["cuerpo"], MARGIN_LEFT, y, CONTENT_W)
        y -= 4*mm

        # Expedición
        y = draw_text_block(
            c,
            "El presente certificado se expide a solicitud del interesado para los fines que estime convenientes.",
            S["cuerpo"], MARGIN_LEFT, y, CONTENT_W
        )

        # Firma
        firma_y = CONTENT_BOT + 36*mm
        cx = PAGE_W / 2

        # Sello decorativo
        c.setStrokeColor(C_GOLD)
        c.setLineWidth(1.5)
        c.circle(cx - 55*mm + 12*mm, firma_y + 8*mm, 12*mm, fill=0, stroke=1)
        c.setFont("Lato-Bold", 5)
        c.setFillColor(C_GOLD)
        c.drawCentredString(cx - 55*mm + 12*mm, firma_y + 6*mm, "PRADNA")
        c.drawCentredString(cx - 55*mm + 12*mm, firma_y + 9*mm, "SEGUROS")

        # Línea y nombre firmante
        c.setStrokeColor(C_PURPLE)
        c.setLineWidth(1)
        c.line(cx - 35*mm, firma_y, cx + 35*mm, firma_y)

        firmante = data.get("firmante", "")
        cargo    = data.get("cargo", "")
        p1 = Paragraph(f"<b>{firmante.upper()}</b>", S["firma_nombre"])
        p2 = Paragraph(cargo, S["firma_detalle"])
        p3 = Paragraph("PRADNA Seguros · Protección que transciende", S["firma_detalle"])

        w1,h1 = p1.wrap(70*mm, 999)
        w2,h2 = p2.wrap(70*mm, 999)
        w3,h3 = p3.wrap(70*mm, 999)
        p1.drawOn(c, cx-35*mm, firma_y - h1 - 2*mm)
        p2.drawOn(c, cx-35*mm, firma_y - h1 - h2 - 4*mm)
        p3.drawOn(c, cx-35*mm, firma_y - h1 - h2 - h3 - 7*mm)

        c.save()
        buf.seek(0)
        return buf.getvalue()
