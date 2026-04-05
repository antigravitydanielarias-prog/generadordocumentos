"""Cuenta de Cobro — Diseño Marca de Agua."""
from __future__ import annotations
import io
from datetime import date
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from core.pdf_builder import (
    draw_branded_page, get_styles, draw_text_block, draw_separator,
    draw_firma, MARGIN_L, MARGIN_R, CONTENT_W, CONTENT_TOP, CONTENT_BOT,
    C_PURPLE, C_PURPLE_DARK, C_GOLD, C_GRAY_LIGHT, PAGE_W, PAGE_H,
    FIRMANTE_NOMBRE, FIRMANTE_CEDULA,
)
from core.document_types.base import BaseDocument


class CuentaCobro(BaseDocument):
    nombre      = "Cuenta de Cobro"
    descripcion = "Cobro de servicios o comisiones con desglose de conceptos."
    icono       = "💰"

    @classmethod
    def get_fields(cls) -> list[dict]:
        return [
            {"key":"num_cuenta",  "label":"Número de cuenta de cobro", "type":"text",
             "required":True, "placeholder":"CC-2025-001", "default":""},
            {"key":"ciudad",      "label":"Ciudad", "type":"text",
             "required":True, "placeholder":"Medellín", "default":"Medellín"},
            {"key":"fecha",       "label":"Fecha", "type":"date",
             "required":True, "default":str(date.today())},
            {"key":"cobrar_a",    "label":"Cobrar a", "type":"text",
             "required":True, "placeholder":"SURA Seguros S.A.", "default":""},
            {"key":"nit_cc",      "label":"NIT / Cédula", "type":"text",
             "required":True, "placeholder":"890.903.790-3", "default":""},
            {"key":"concepto1",   "label":"Concepto 1", "type":"text",
             "required":True, "placeholder":"Comisión póliza de vida", "default":""},
            {"key":"valor1",      "label":"Valor 1 (solo número)", "type":"number",
             "required":True, "placeholder":"500000", "default":""},
            {"key":"concepto2",   "label":"Concepto 2 (opcional)", "type":"text",
             "required":False, "placeholder":"", "default":""},
            {"key":"valor2",      "label":"Valor 2 (opcional)", "type":"number",
             "required":False, "placeholder":"0", "default":""},
            {"key":"concepto3",   "label":"Concepto 3 (opcional)", "type":"text",
             "required":False, "placeholder":"", "default":""},
            {"key":"valor3",      "label":"Valor 3 (opcional)", "type":"number",
             "required":False, "placeholder":"0", "default":""},
            {"key":"banco",       "label":"Banco", "type":"text",
             "required":False, "placeholder":"Bancolombia", "default":""},
            {"key":"cuenta_banco","label":"Número de cuenta bancaria", "type":"text",
             "required":False, "placeholder":"123-456789-00", "default":""},
            {"key":"tipo_cuenta", "label":"Tipo de cuenta", "type":"select",
             "options":["Ahorros","Corriente"], "required":False, "default":"Ahorros"},
        ]

    @classmethod
    def build_pdf(cls, data: dict, numero: str) -> bytes:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
        draw_branded_page(c, numero)
        S = get_styles()
        y = CONTENT_TOP

        y = draw_text_block(c, "Cuenta de Cobro", S["titulo"], MARGIN_L, y, CONTENT_W)

        try:
            from datetime import datetime
            dt = datetime.strptime(data.get("fecha", str(date.today())), "%Y-%m-%d")
            fecha_str = f"{data.get('ciudad','Medellín')}, {dt.strftime('%d de %B de %Y').capitalize()}"
        except Exception:
            fecha_str = f"{data.get('ciudad','')}, {data.get('fecha','')}"

        y = draw_text_block(c, fecha_str, S["fecha"], MARGIN_L, y, CONTENT_W)
        y = draw_separator(c, y)
        y -= 4*mm

        half = CONTENT_W / 2 - 5*mm
        right_x = MARGIN_L + half + 10*mm
        y_l = draw_text_block(c,"COBRAR A",S["etiqueta"],MARGIN_L,y,half)
        y_l = draw_text_block(c,data.get("cobrar_a",""),S["valor"],MARGIN_L,y_l,half)
        y_l = draw_text_block(c,"NIT / CÉDULA",S["etiqueta"],MARGIN_L,y_l,half)
        y_l = draw_text_block(c,data.get("nit_cc",""),S["valor"],MARGIN_L,y_l,half)
        y_r = draw_text_block(c,"N° CUENTA DE COBRO",S["etiqueta"],right_x,y,half)
        y_r = draw_text_block(c,data.get("num_cuenta",""),S["valor"],right_x,y_r,half)
        y = min(y_l, y_r) - 6*mm
        y = draw_separator(c, y); y -= 4*mm

        def fmt(v):
            try: return "$ {:,.0f}".format(float(str(v).replace(",","")))
            except: return str(v) if v else "—"

        rows = [["CONCEPTO","VALOR"]]; total = 0
        for i in range(1,4):
            con = data.get(f"concepto{i}","").strip()
            val = data.get(f"valor{i}","")
            if con and val:
                try: v=float(str(val).replace(",","")); total+=v; rows.append([con,fmt(v)])
                except: rows.append([con,val]) if con else None
        rows.append(["TOTAL",fmt(total)])

        col_w = [CONTENT_W*0.68, CONTENT_W*0.32]
        tbl = Table(rows, colWidths=col_w)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),C_PURPLE),("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),9),
            ("ALIGN",(1,0),(1,-1),"RIGHT"),("ALIGN",(0,0),(0,-1),"LEFT"),
            ("FONTNAME",(0,1),(-1,-2),"Helvetica"),("FONTSIZE",(0,1),(-1,-2),10),
            ("ROWBACKGROUNDS",(0,1),(-1,-2),[colors.white,colors.HexColor("#F4F1F9")]),
            ("BACKGROUND",(0,-1),(-1,-1),C_GOLD),
            ("TEXTCOLOR",(0,-1),(-1,-1),C_PURPLE_DARK),
            ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),("FONTSIZE",(0,-1),(-1,-1),11),
            ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#D8D0EC")),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("LEFTPADDING",(0,0),(-1,-1),8),
        ]))
        tw, th = tbl.wrap(CONTENT_W, 999)
        tbl.drawOn(c, MARGIN_L, y - th); y = y - th - 8*mm

        banco = data.get("banco",""); cta = data.get("cuenta_banco","")
        if banco or cta:
            y = draw_separator(c, y); y -= 2*mm
            y = draw_text_block(c,"DATOS BANCARIOS",S["etiqueta"],MARGIN_L,y,CONTENT_W)
            if banco:
                y = draw_text_block(c,f"Banco: <b>{banco}</b> · Cuenta {data.get('tipo_cuenta','Ahorros')}: <b>{cta}</b>",
                                   S["normal"],MARGIN_L,y,CONTENT_W)

        draw_firma(c, CONTENT_BOT + 38*mm)
        c.save(); buf.seek(0)
        return buf.getvalue()
