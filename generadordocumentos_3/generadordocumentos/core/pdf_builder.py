"""
core/pdf_builder.py — Motor PDF · PRADNA Seguros
Diseño: Marca de agua (elefante SVG translúcido de fondo)
Logo: Isologo completo SVG sin fondo
Firmante fijo: Yohanna Catalina Henao Herrera
"""
from __future__ import annotations

import io
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


# ── Rutas ─────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
FONTS_DIR  = BASE_DIR / "fonts"
ASSETS_DIR = BASE_DIR / "assets"

# ── Paleta PRADNA ─────────────────────────────────────────────────────────────
C_PURPLE      = colors.HexColor("#341E52")
C_PURPLE_DARK = colors.HexColor("#1A0F30")
C_PURPLE_MID  = colors.HexColor("#5C3D8A")
C_GOLD        = colors.HexColor("#C8A84B")
C_GOLD_LIGHT  = colors.HexColor("#E8C86B")
C_GRAY        = colors.HexColor("#6B5B8A")
C_GRAY_LIGHT  = colors.HexColor("#F4F1F9")
C_BLACK       = colors.HexColor("#1A1A2E")
C_WHITE       = colors.white

PAGE_W, PAGE_H = A4   # 595.27 × 841.89 pt

# ── Firmante fijo ──────────────────────────────────────────────────────────────
FIRMANTE_NOMBRE = "Yohanna Catalina Henao Herrera"
FIRMANTE_CEDULA = "C.C. 32.242.333"
FIRMANTE_CARGO  = "Asesora Comercial · PRADNA Seguros"

# ── Márgenes y zonas ──────────────────────────────────────────────────────────
MARGIN_L   = 20 * mm
MARGIN_R   = 20 * mm
MARGIN_T   = 22 * mm   # debajo del header
MARGIN_B   = 28 * mm   # encima del footer
CONTENT_W  = PAGE_W - MARGIN_L - MARGIN_R
CONTENT_TOP = PAGE_H - MARGIN_T
CONTENT_BOT = MARGIN_B

# ── Fuentes ───────────────────────────────────────────────────────────────────
_FONT_FALLBACKS = {
    "Lato-Regular":    "Helvetica",
    "Lato-Bold":       "Helvetica-Bold",
    "Lato-Black":      "Helvetica-Bold",
    "Lato-Light":      "Helvetica",
    "Lato-Italic":     "Helvetica-Oblique",
    "Lato-BoldItalic": "Helvetica-BoldOblique",
}
_fonts_loaded = False

def _load_fonts():
    global _fonts_loaded
    if _fonts_loaded:
        return
    font_map = {
        "Lato-Regular":    "Lato-Regular.ttf",
        "Lato-Bold":       "Lato-Bold.ttf",
        "Lato-Black":      "Lato-Black.ttf",
        "Lato-Light":      "Lato-Light.ttf",
        "Lato-Italic":     "Lato-Italic.ttf",
        "Lato-BoldItalic": "Lato-BoldItalic.ttf",
    }
    for name, fname in font_map.items():
        p = FONTS_DIR / fname
        if p.exists():
            try:
                pdfmetrics.registerFont(TTFont(name, str(p)))
            except Exception:
                pass
    _fonts_loaded = True

def F(name: str) -> str:
    """Retorna nombre de fuente disponible con fallback."""
    _load_fonts()
    try:
        pdfmetrics.getFont(name)
        return name
    except Exception:
        return _FONT_FALLBACKS.get(name, "Helvetica")


# ── Estilos de texto ──────────────────────────────────────────────────────────

def get_styles() -> dict[str, ParagraphStyle]:
    _load_fonts()
    return {
        "titulo": ParagraphStyle("titulo",
            fontName=F("Lato-Black"), fontSize=34, leading=40,
            textColor=C_PURPLE, spaceAfter=3*mm,
        ),
        "subtitulo": ParagraphStyle("subtitulo",
            fontName=F("Lato-Bold"), fontSize=13, leading=17,
            textColor=C_PURPLE_MID, spaceAfter=5*mm,
        ),
        "ref": ParagraphStyle("ref",
            fontName=F("Lato-Light"), fontSize=9, leading=13,
            textColor=C_GRAY, spaceAfter=4*mm,
        ),
        "normal": ParagraphStyle("normal",
            fontName=F("Lato-Regular"), fontSize=11, leading=18,
            textColor=C_BLACK, spaceAfter=4*mm,
        ),
        "bold": ParagraphStyle("bold",
            fontName=F("Lato-Bold"), fontSize=11, leading=18,
            textColor=C_BLACK, spaceAfter=4*mm,
        ),
        "cuerpo": ParagraphStyle("cuerpo",
            fontName=F("Lato-Regular"), fontSize=11, leading=19,
            textColor=C_BLACK, spaceAfter=5*mm, alignment=4,
        ),
        "etiqueta": ParagraphStyle("etiqueta",
            fontName=F("Lato-Bold"), fontSize=8, leading=11,
            textColor=C_GOLD, spaceBefore=3*mm,
        ),
        "valor": ParagraphStyle("valor",
            fontName=F("Lato-Regular"), fontSize=11, leading=15,
            textColor=C_BLACK,
        ),
        "firma_nombre": ParagraphStyle("firma_nombre",
            fontName=F("Lato-Bold"), fontSize=11, leading=14,
            textColor=C_PURPLE, alignment=1,
        ),
        "firma_detalle": ParagraphStyle("firma_detalle",
            fontName=F("Lato-Regular"), fontSize=9, leading=13,
            textColor=C_GRAY, alignment=1,
        ),
        "fecha": ParagraphStyle("fecha",
            fontName=F("Lato-Light"), fontSize=9, leading=13,
            textColor=C_GRAY, spaceAfter=5*mm,
        ),
        "small": ParagraphStyle("small",
            fontName=F("Lato-Regular"), fontSize=8, leading=11,
            textColor=C_GRAY,
        ),
    }


# ── Helpers de dibujo ─────────────────────────────────────────────────────────

def _draw_watermark_elephant(c: canvas.Canvas):
    """
    Elefante PNG como marca de agua centrada en la página.
    Opacity baja para no interferir con el texto.
    """
    wm_path = ASSETS_DIR / "elefante_watermark.png"
    if not wm_path.exists():
        _draw_fallback_watermark(c)
        return
    try:
        # Tamaño: ~65% del ancho de página
        target_w = PAGE_W * 0.65
        target_h = target_w * (837 / 1128)  # proporción del elefante
        x = (PAGE_W - target_w) / 2
        y = (PAGE_H - target_h) / 2 - 15*mm
        c.saveState()
        c.setFillAlpha(0.07)
        c.drawImage(
            str(wm_path), x, y,
            width=target_w, height=target_h,
            preserveAspectRatio=True, mask="auto",
        )
        c.restoreState()
    except Exception:
        _draw_fallback_watermark(c)

def _draw_fallback_watermark(c: canvas.Canvas):
    """Elefante vectorial simple si no hay SVG."""
    cx = PAGE_W / 2
    cy = PAGE_H / 2 - 15*mm
    c.saveState()
    c.setStrokeColor(C_PURPLE)
    c.setLineWidth(8)
    c.setStrokeAlpha(0.05)
    # Cuerpo
    c.ellipse(cx-60*mm, cy-35*mm, cx+60*mm, cy+35*mm, fill=0, stroke=1)
    # Cabeza
    c.ellipse(cx+30*mm, cy+20*mm, cx+70*mm, cy+55*mm, fill=0, stroke=1)
    # Trompa
    c.arc(cx+40*mm, cy-20*mm, cx+90*mm, cy+30*mm, startAng=180, extent=-120)
    c.restoreState()

def _draw_header(c: canvas.Canvas, numero: str):
    """Header minimalista: ref izquierda, fecha derecha, línea dorada."""
    _load_fonts()
    # Línea dorada superior
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(1.5)
    c.line(MARGIN_L, PAGE_H - 10*mm, PAGE_W - MARGIN_R, PAGE_H - 10*mm)

    # Ref número
    c.setFont(F("Lato-Regular"), 8)
    c.setFillColor(C_GRAY)
    if numero:
        c.drawString(MARGIN_L, PAGE_H - 8*mm, numero)

    # Logo en header derecho
    _draw_logo_header(c)

def _draw_logo_header(c: canvas.Canvas):
    """Logo PRADNA completo PNG en esquina superior derecha."""
    logo_png = ASSETS_DIR / "logo_pradna_clean.png"
    if not logo_png.exists():
        logo_png = ASSETS_DIR / "logo_pradna.png"
    if logo_png.exists():
        logo_w = 42*mm
        logo_h = 13*mm
        c.drawImage(
            str(logo_png),
            PAGE_W - MARGIN_R - logo_w,
            PAGE_H - 9*mm,
            width=logo_w, height=logo_h,
            preserveAspectRatio=True,
            mask=[0, 10, 0, 10, 0, 10],  # remove near-black background
        )
    else:
        # Texto fallback
        c.setFont(F("Lato-Black"), 11)
        c.setFillColor(C_PURPLE)
        c.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 7*mm, "PRADNA SEGUROS")

def _draw_footer(c: canvas.Canvas):
    """Footer con línea, logo centrado y tagline."""
    _load_fonts()
    # Línea separadora
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(0.5)
    c.setStrokeAlpha(0.4)
    c.line(MARGIN_L, MARGIN_B, PAGE_W - MARGIN_R, MARGIN_B)
    c.setStrokeAlpha(1)

    # Logo centrado en footer
    logo_png = ASSETS_DIR / "logo_pradna_clean.png"
    if not logo_png.exists():
        logo_png = ASSETS_DIR / "logo_pradna.png"
    logo_w = 38*mm
    logo_h = 12*mm
    if logo_png.exists():
        c.drawImage(
            str(logo_png),
            (PAGE_W - logo_w) / 2,
            MARGIN_B - logo_h - 1*mm,
            width=logo_w, height=logo_h,
            preserveAspectRatio=True,
            mask=[0, 10, 0, 10, 0, 10],
        )
    else:
        c.setFont(F("Lato-Bold"), 9)
        c.setFillColor(C_PURPLE)
        c.drawCentredString(PAGE_W/2, MARGIN_B - 8*mm, "PRADNA SEGUROS")

    # Tagline
    c.setFont(F("Lato-Light"), 7)
    c.setFillColor(C_GOLD)
    c.drawCentredString(PAGE_W/2, MARGIN_B - logo_h - 5*mm, "Protección que transciende")

def _draw_separator(c: canvas.Canvas, y: float) -> float:
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(1)
    c.setStrokeAlpha(0.5)
    c.line(MARGIN_L, y, PAGE_W - MARGIN_R, y)
    c.setStrokeAlpha(1)
    return y - 5*mm

def _draw_firma(c: canvas.Canvas, y_firma: float):
    """Bloque de firma fijo de Yohanna + espacio para firma del cliente."""
    _load_fonts()
    cx_firma = PAGE_W / 2

    # Línea de firma
    c.setStrokeColor(C_PURPLE)
    c.setLineWidth(0.75)
    c.line(cx_firma - 40*mm, y_firma, cx_firma + 40*mm, y_firma)

    S = get_styles()
    p1 = Paragraph(f"<b>{FIRMANTE_NOMBRE.upper()}</b>", S["firma_nombre"])
    p2 = Paragraph(FIRMANTE_CEDULA, S["firma_detalle"])
    p3 = Paragraph(FIRMANTE_CARGO, S["firma_detalle"])
    w, h1 = p1.wrap(80*mm, 999)
    w, h2 = p2.wrap(80*mm, 999)
    w, h3 = p3.wrap(80*mm, 999)
    p1.drawOn(c, cx_firma - 40*mm, y_firma - h1 - 2*mm)
    p2.drawOn(c, cx_firma - 40*mm, y_firma - h1 - h2 - 4*mm)
    p3.drawOn(c, cx_firma - 40*mm, y_firma - h1 - h2 - h3 - 6*mm)


# ── API pública ───────────────────────────────────────────────────────────────

def draw_branded_page(c: canvas.Canvas, numero: str = ""):
    """Dibuja todos los elementos de branding sobre la página actual."""
    _draw_watermark_elephant(c)
    _draw_header(c, numero)
    _draw_footer(c)


def draw_text_block(c: canvas.Canvas, text: str, style: ParagraphStyle,
                    x: float, y: float, max_width: float) -> float:
    para = Paragraph(text, style)
    w, h = para.wrap(max_width, 9999)
    para.drawOn(c, x, y - h)
    return y - h - (style.spaceAfter or 0)


def draw_separator(c: canvas.Canvas, y: float) -> float:
    return _draw_separator(c, y)


def draw_firma(c: canvas.Canvas, y: float):
    _draw_firma(c, y)


def format_value(value, field_format: str = "auto") -> str:
    import pandas as pd
    if pd.isna(value) or str(value).strip() in ("nan", "NaT", "None", ""):
        return ""
    v = str(value).strip()
    MESES = {1:"enero",2:"febrero",3:"marzo",4:"abril",5:"mayo",6:"junio",
             7:"julio",8:"agosto",9:"septiembre",10:"octubre",11:"noviembre",12:"diciembre"}
    if field_format == "currency":
        try: return "$ {:,.0f}".format(float(v)).replace(",",".")
        except: return v
    if field_format == "date":
        try: return pd.to_datetime(value).strftime("%Y-%m-%d")
        except: return v
    if field_format == "date_long":
        try:
            dt = pd.to_datetime(value)
            return f"{dt.day} de {MESES[dt.month]} de {dt.year}"
        except: return v
    if field_format == "percent":
        try: return "{:.2f}%".format(float(v))
        except: return v
    return v
