"""
core/pdf_builder.py — Motor de generación PDF · PRADNA Seguros
--------------------------------------------------------------
Genera documentos con el branding PRADNA: ondas decorativas,
tipografía Lato, logo institucional. Base para todos los tipos
de documento.
"""
from __future__ import annotations

import io
from datetime import date
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
BASE_DIR  = Path(__file__).parent.parent
FONTS_DIR = BASE_DIR / "fonts"
ASSETS_DIR = BASE_DIR / "assets"

# ── Paleta PRADNA ─────────────────────────────────────────────────────────────
C_PURPLE_DARK  = colors.HexColor("#1A0F30")
C_PURPLE       = colors.HexColor("#341E52")
C_PURPLE_MID   = colors.HexColor("#5C3D8A")
C_GOLD         = colors.HexColor("#C8A84B")
C_GOLD_LIGHT   = colors.HexColor("#E8C86B")
C_WHITE        = colors.white
C_BLACK        = colors.HexColor("#1A1A2E")
C_GRAY         = colors.HexColor("#6B5B8A")
C_GRAY_LIGHT   = colors.HexColor("#F4F1F9")

PAGE_W, PAGE_H = A4   # 595.27 x 841.89 pt

# ── Registro de fuentes ───────────────────────────────────────────────────────
_fonts_loaded = False

def _load_fonts():
    global _fonts_loaded
    if _fonts_loaded:
        return
    font_map = {
        "Lato-Regular":   "Lato-Regular.ttf",
        "Lato-Bold":      "Lato-Bold.ttf",
        "Lato-Black":     "Lato-Black.ttf",
        "Lato-Light":     "Lato-Light.ttf",
        "Lato-Italic":    "Lato-Italic.ttf",
        "Lato-BoldItalic":"Lato-BoldItalic.ttf",
        # HRounded-Bold: OTF not supported by ReportLab (postscript outlines)
    }
    for name, filename in font_map.items():
        path = FONTS_DIR / filename
        if path.exists():
            try:
                pdfmetrics.registerFont(TTFont(name, str(path)))
            except Exception:
                pass
    _fonts_loaded = True


# ── Helpers de dibujo ─────────────────────────────────────────────────────────

def _draw_wave_top(c: canvas.Canvas):
    """Onda decorativa superior derecha — dorada con acento morado."""
    # Onda dorada principal (esquina sup derecha)
    p = c.beginPath()
    p.moveTo(PAGE_W * 0.45, PAGE_H)
    p.curveTo(PAGE_W * 0.55, PAGE_H * 0.97,
              PAGE_W * 0.75, PAGE_H * 0.98,
              PAGE_W,        PAGE_H * 0.95)
    p.lineTo(PAGE_W, PAGE_H)
    p.close()
    c.setFillColor(C_GOLD)
    c.drawPath(p, fill=1, stroke=0)

    # Acento morado sobre la onda dorada
    p2 = c.beginPath()
    p2.moveTo(PAGE_W * 0.62, PAGE_H)
    p2.curveTo(PAGE_W * 0.72, PAGE_H * 0.985,
               PAGE_W * 0.88, PAGE_H * 0.992,
               PAGE_W,        PAGE_H * 0.972)
    p2.lineTo(PAGE_W, PAGE_H)
    p2.close()
    c.setFillColor(C_PURPLE)
    c.drawPath(p2, fill=1, stroke=0)

    # Pequeña onda dorada esquina sup izquierda
    p3 = c.beginPath()
    p3.moveTo(0, PAGE_H)
    p3.curveTo(20*mm, PAGE_H * 0.985,
               40*mm, PAGE_H * 0.992,
               55*mm, PAGE_H * 0.978)
    p3.curveTo(40*mm, PAGE_H * 0.97,
               20*mm, PAGE_H * 0.975,
               0, PAGE_H * 0.968)
    p3.close()
    c.setFillColor(C_GOLD)
    c.drawPath(p3, fill=1, stroke=0)


def _draw_wave_bottom(c: canvas.Canvas):
    """Ondas decorativas inferiores — dorada izquierda, morada derecha."""
    # Onda dorada inferior izquierda
    p = c.beginPath()
    p.moveTo(0, 0)
    p.lineTo(PAGE_W * 0.55, 0)
    p.curveTo(PAGE_W * 0.42, 18*mm,
              PAGE_W * 0.22, 22*mm,
              0,             16*mm)
    p.close()
    c.setFillColor(C_GOLD)
    c.drawPath(p, fill=1, stroke=0)

    # Onda morada inferior derecha
    p2 = c.beginPath()
    p2.moveTo(PAGE_W, 0)
    p2.lineTo(PAGE_W * 0.38, 0)
    p2.curveTo(PAGE_W * 0.52, 20*mm,
               PAGE_W * 0.72, 25*mm,
               PAGE_W,        18*mm)
    p2.close()
    c.setFillColor(C_PURPLE_DARK)
    c.drawPath(p2, fill=1, stroke=0)

    # Acento dorado pequeño esquina inf derecha
    p3 = c.beginPath()
    p3.moveTo(PAGE_W, 0)
    p3.lineTo(PAGE_W * 0.72, 0)
    p3.curveTo(PAGE_W * 0.80, 8*mm,
               PAGE_W * 0.90, 10*mm,
               PAGE_W,        8*mm)
    p3.close()
    c.setFillColor(C_GOLD)
    c.drawPath(p3, fill=1, stroke=0)


def _draw_logo(c: canvas.Canvas):
    """Logo PRADNA vectorial en la parte inferior central."""
    logo_path = ASSETS_DIR / "logo_pradna.png"
    cx = PAGE_W / 2
    cy = 28*mm
    logo_w = 52*mm
    logo_h = 18*mm

    if logo_path.exists():
        c.drawImage(
            str(logo_path),
            cx - logo_w/2, cy - logo_h/2,
            width=logo_w, height=logo_h,
            preserveAspectRatio=True, mask="auto"
        )
    else:
        # Logo vectorial de respaldo
        # Elipse con elefante simplificado
        c.setFillColor(C_PURPLE)
        c.ellipse(cx - 30*mm, cy - 8*mm, cx - 14*mm, cy + 8*mm, fill=1, stroke=0)

        # Texto PRADNA
        c.setFont("Lato-Black" if _fonts_loaded else "Helvetica-Bold", 16)
        c.setFillColor(C_PURPLE)
        c.drawString(cx - 10*mm, cy + 2*mm, "PRADNA")
        c.setFont("Lato-Regular" if _fonts_loaded else "Helvetica", 7)
        c.setFillColor(C_GRAY)
        c.drawCentredString(cx + 10*mm, cy - 3*mm, "S E G U R O S")
        c.setFont("Lato-Light" if _fonts_loaded else "Helvetica", 6)
        c.setFillColor(C_GOLD)
        c.drawCentredString(cx + 10*mm, cy - 8*mm, "Protección que transciende")


def _draw_doc_number(c: canvas.Canvas, numero: str):
    """Número de documento en esquina superior izquierda."""
    c.setFont("Lato-Regular" if _fonts_loaded else "Helvetica", 7)
    c.setFillColor(C_GRAY)
    c.drawString(18*mm, PAGE_H - 12*mm, f"Ref. {numero}")


def draw_branded_page(c: canvas.Canvas, numero: str = ""):
    """
    Dibuja todos los elementos de branding PRADNA en la página actual.
    Llamar ANTES de dibujar el contenido del documento.
    """
    _load_fonts()
    _draw_wave_top(c)
    _draw_wave_bottom(c)
    _draw_logo(c)
    if numero:
        _draw_doc_number(c, numero)


# ── Estilos de párrafo ────────────────────────────────────────────────────────

def get_styles() -> dict[str, ParagraphStyle]:
    _load_fonts()
    base = dict(
        fontName="Lato-Regular",
        fontSize=10,
        leading=16,
        textColor=C_BLACK,
        spaceAfter=4*mm,
    )
    return {
        "titulo": ParagraphStyle("titulo",
            fontName="Lato-Black", fontSize=32, leading=38,
            textColor=C_PURPLE, spaceAfter=10*mm, spaceBefore=2*mm,
        ),
        "subtitulo": ParagraphStyle("subtitulo",
            fontName="Lato-Bold", fontSize=14, leading=18,
            textColor=C_PURPLE_MID, spaceAfter=6*mm,
        ),
        "normal": ParagraphStyle("normal", **base),
        "bold": ParagraphStyle("bold",
            **{**base, "fontName": "Lato-Bold"}),
        "small": ParagraphStyle("small",
            **{**base, "fontSize": 8, "leading": 12, "textColor": C_GRAY}),
        "firma_nombre": ParagraphStyle("firma_nombre",
            fontName="Lato-Bold", fontSize=11, leading=14,
            textColor=C_PURPLE, alignment=1,
        ),
        "firma_detalle": ParagraphStyle("firma_detalle",
            fontName="Lato-Regular", fontSize=9, leading=12,
            textColor=C_GRAY, alignment=1,
        ),
        "etiqueta": ParagraphStyle("etiqueta",
            fontName="Lato-Bold", fontSize=8, leading=11,
            textColor=C_GOLD, spaceBefore=3*mm,
        ),
        "valor": ParagraphStyle("valor",
            fontName="Lato-Regular", fontSize=10, leading=14,
            textColor=C_BLACK,
        ),
        "cuerpo": ParagraphStyle("cuerpo",
            fontName="Lato-Regular", fontSize=10, leading=17,
            textColor=C_BLACK, spaceAfter=5*mm, alignment=4,  # justify
        ),
        "fecha": ParagraphStyle("fecha",
            fontName="Lato-Light", fontSize=9, leading=13,
            textColor=C_GRAY, spaceAfter=6*mm,
        ),
    }


# ── Área de contenido ─────────────────────────────────────────────────────────

MARGIN_LEFT  = 18*mm
MARGIN_RIGHT = 18*mm
CONTENT_TOP  = PAGE_H - 38*mm   # debajo de las ondas superiores
CONTENT_BOT  = 48*mm            # encima del logo y ondas inferiores
CONTENT_W    = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT


def draw_text_block(c: canvas.Canvas, text: str, style: ParagraphStyle,
                    x: float, y: float, max_width: float) -> float:
    """
    Dibuja un bloque de texto con wrapping. Retorna la Y resultante (hacia abajo).
    """
    para = Paragraph(text, style)
    w, h = para.wrap(max_width, 9999)
    para.drawOn(c, x, y - h)
    return y - h - style.spaceAfter


def draw_separator(c: canvas.Canvas, y: float, alpha: float = 0.15) -> float:
    """Línea separadora dorada tenue."""
    c.setStrokeColor(C_GOLD)
    c.setLineWidth(0.5)
    c.setFillAlpha(alpha)
    c.line(MARGIN_LEFT, y, PAGE_W - MARGIN_RIGHT, y)
    c.setFillAlpha(1)
    return y - 4*mm


def draw_field_pair(c: canvas.Canvas, label: str, value: str,
                    x: float, y: float, styles: dict,
                    col_w: float | None = None) -> float:
    """Dibuja un par etiqueta + valor apilados verticalmente."""
    cw = col_w or CONTENT_W
    y = draw_text_block(c, label.upper(), styles["etiqueta"], x, y, cw)
    y = draw_text_block(c, value or "—", styles["valor"], x, y, cw)
    return y - 2*mm
