"""Cuenta de Cobro."""
from __future__ import annotations
import io
from datetime import date
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from core.pdf_builder import (
    draw_branded_page, get_styles, draw_text_block, draw_separator,
    MARGIN_LEFT, MARGIN_RIGHT, CONTENT_TOP, CONTENT_W, CONTENT_BOT,
    C_PURPLE, C_GOLD, C_PURPLE_DARK, C_GRAY_LIGHT, PAGE_W, PAGE_H,
)
from core.document_types.base import BaseDocument


class CuentaCobro(BaseDocument):
    nombre      = "Cuenta de Cobro"
    descripcion = "Documento de cobro de servicios o comisiones con desglose de conceptos."
    icono       = "💰"

    @classmethod
    def get_fields(cls) -> list[dict]:
        return [
            {"key": "num_cuenta",   "label": "Número de cuenta de cobro", "type": "text",
             "required": True, "placeholder": "CC-2025-001", "default": ""},
            {"key": "ciudad",       "label": "Ciudad", "type": "text",
             "required": True, "placeholder": "Medellín", "default": "Medellín"},
            {"key": "fecha",        "label": "Fecha", "type": "date",
             "required": True, "default": str(date.today())},
            {"key": "cobrar_a",     "label": "Cobrar a (empresa/persona)", "type": "text",
             "required": True, "placeholder": "Nombre del cliente o empresa", "default": ""},
            {"key": "nit_cc",       "label": "NIT / Cédula del destinatario", "type": "text",
             "required": True, "placeholder": "900.123.456-1", "default": ""},
            {"key": "concepto1",    "label": "Concepto 1", "type": "text",
             "required": True, "placeholder": "Ej: Comisión póliza de vida", "default": ""},
            {"key": "valor1",       "label": "Valor 1 (solo número)", "type": "number",
             "required": True, "placeholder": "500000", "default": ""},
            {"key": "concepto2",    "label": "Concepto 2 (opcional)", "type": "text",
             "required": False, "placeholder": "", "default": ""},
            {"key": "valor2",       "label": "Valor 2 (opcional)", "type": "number",
             "required": False, "placeholder": "0", "default": ""},
            {"key": "concepto3",    "label": "Concepto 3 (opcional)", "type": "text",
             "required": False, "placeholder": "", "default": ""},
            {"key": "valor3",       "label": "Valor 3 (opcional)", "type": "number",
             "required": False, "placeholder": "0", "default": ""},
            {"key": "cobrador",     "label": "Nombre del cobrador", "type": "text",
             "required": True, "placeholder": "Tu nombre completo", "default": ""},
            {"key": "cedula_cobrador","label": "Cédula del cobrador","type": "text",
             "required": True, "placeholder": "1036647333", "default": ""},
            {"key": "banco",        "label": "Banco", "type": "text",
             "required": False, "placeholder": "Bancolombia", "default": ""},
            {"key": "cuenta_banco", "label": "Número de cuenta bancaria", "type": "text",
             "required": False, "placeholder": "123-456789-00", "default": ""},
            {"key": "tipo_cuenta",  "label": "Tipo de cuenta", "type": "select",
             "options": ["Ahorros","Corriente"], "required": False, "default": "Ahorros"},
        ]

    @classmethod
    def build_pdf(cls, data: dict, numero: str) -> bytes:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
        draw_branded_page(c, numero)
        S = get_styles()

        y = CONTENT_TOP

        # Título + número
        y = draw_text_block(c, "Cuenta de Cobro", S["titulo"], MARGIN_LEFT, y, CONTENT_W)

        try:
            from datetime import datetime
            dt = datetime.strptime(data.get("fecha", str(date.today())), "%Y-%m-%d")
            fecha_str = f"{data.get('ciudad','Medellín')}, {dt.strftime('%d de %B de %Y').capitalize()}"
        except Exception:
            fecha_str = f"{data.get('ciudad','')}, {data.get('fecha','')}"

        y = draw_text_block(c, fecha_str, S["fecha"], MARGIN_LEFT, y, CONTENT_W)
        y -= 2*mm

        # Ref y destinatario en dos columnas
        half = CONTENT_W / 2 - 5*mm
        left_x  = MARGIN_LEFT
        right_x = MARGIN_LEFT + half + 10*mm

        # Cobrar a
        y_l = draw_text_block(c, "COBRAR A", S["etiqueta"], left_x, y, half)
        y_l = draw_text_block(c, data.get("cobrar_a",""), S["valor"], left_x, y_l, half)
        y_l = draw_text_block(c, "NIT / CÉDULA", S["etiqueta"], left_x, y_l, half)
        y_l = draw_text_block(c, data.get("nit_cc",""), S["valor"], left_x, y_l, half)

        y_r = draw_text_block(c, "N° CUENTA DE COBRO", S["etiqueta"], right_x, y, half)
        y_r = draw_text_block(c, data.get("num_cuenta",""), S["valor"], right_x, y_r, half)

        y = min(y_l, y_r) - 4*mm
        y = draw_separator(c, y)
        y -= 4*mm

        # Tabla de conceptos
        def fmt_money(val):
            try:
                return "$ {:,.0f}".format(float(str(val).replace(",","")))
            except Exception:
                return val or "—"

        rows = [["CONCEPTO", "VALOR"]]
        total = 0
        for i in range(1, 4):
            con = data.get(f"concepto{i}", "").strip()
            val = data.get(f"valor{i}", "")
            if con and val:
                try:
                    v = float(str(val).replace(",",""))
                    total += v
                    rows.append([con, fmt_money(v)])
                except Exception:
                    if con:
                        rows.append([con, val])

        rows.append(["TOTAL", fmt_money(total)])

        col_widths = [CONTENT_W * 0.68, CONTENT_W * 0.32]
        tbl = Table(rows, colWidths=col_widths)
        tbl.setStyle(TableStyle([
            # Header
            ("BACKGROUND",  (0,0), (-1,0),  C_PURPLE),
            ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
            ("FONTNAME",    (0,0), (-1,0),  "Lato-Bold"),
            ("FONTSIZE",    (0,0), (-1,0),  9),
            ("ALIGN",       (1,0), (1,-1),  "RIGHT"),
            ("ALIGN",       (0,0), (0,-1),  "LEFT"),
            # Filas
            ("FONTNAME",    (0,1), (-1,-2), "Lato-Regular"),
            ("FONTSIZE",    (0,1), (-1,-2), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-2),[colors.white, C_GRAY_LIGHT]),
            # Total
            ("BACKGROUND",  (0,-1),(-1,-1), C_GOLD),
            ("TEXTCOLOR",   (0,-1),(-1,-1), C_PURPLE_DARK),
            ("FONTNAME",    (0,-1),(-1,-1), "Lato-Bold"),
            ("FONTSIZE",    (0,-1),(-1,-1), 11),
            # Bordes
            ("GRID",        (0,0), (-1,-1), 0.25, colors.HexColor("#D8D0EC")),
            ("TOPPADDING",  (0,0), (-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
        ]))

        tw, th = tbl.wrap(CONTENT_W, 999)
        tbl.drawOn(c, MARGIN_LEFT, y - th)
        y = y - th - 8*mm

        # Datos bancarios
        banco     = data.get("banco","")
        cta_banco = data.get("cuenta_banco","")
        tipo_cta  = data.get("tipo_cuenta","")
        if banco or cta_banco:
            y = draw_separator(c, y)
            y -= 2*mm
            y = draw_text_block(c, "DATOS BANCARIOS", S["etiqueta"], MARGIN_LEFT, y, CONTENT_W)
            if banco:
                y = draw_text_block(c, f"Banco: <b>{banco}</b> · Cuenta {tipo_cta}: <b>{cta_banco}</b>",
                                    S["normal"], MARGIN_LEFT, y, CONTENT_W)

        # Firma
        firma_y = CONTENT_BOT + 32*mm
        cx = PAGE_W / 2
        c.setStrokeColor(C_PURPLE)
        c.setLineWidth(1)
        c.line(cx - 35*mm, firma_y, cx + 35*mm, firma_y)

        cobrador = data.get("cobrador","")
        ced      = data.get("cedula_cobrador","")
        p1 = Paragraph(f"<b>{cobrador.upper()}</b>", S["firma_nombre"])
        p2 = Paragraph(f"C.C. {ced}", S["firma_detalle"])
        w1,h1 = p1.wrap(70*mm,999)
        w2,h2 = p2.wrap(70*mm,999)
        p1.drawOn(c, cx-35*mm, firma_y-h1-2*mm)
        p2.drawOn(c, cx-35*mm, firma_y-h1-h2-4*mm)

        c.save()
        buf.seek(0)
        return buf.getvalue()
