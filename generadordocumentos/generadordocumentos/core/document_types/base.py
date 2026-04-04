"""core/document_types/base.py — Clase base para todos los tipos de documento."""
from __future__ import annotations
from abc import ABC, abstractmethod
import io
from reportlab.pdfgen import canvas
from core.pdf_builder import PAGE_W, PAGE_H, draw_branded_page


class BaseDocument(ABC):
    """Clase base que todos los tipos de documento deben extender."""

    # Metadatos del tipo (definir en cada subclase)
    nombre: str = "Documento"
    descripcion: str = ""
    icono: str = "📄"

    @classmethod
    @abstractmethod
    def get_fields(cls) -> list[dict]:
        """
        Retorna la definición de campos del formulario.
        Cada campo es un dict con:
          - key: str           → identificador único
          - label: str         → etiqueta en el formulario
          - type: str          → "text" | "textarea" | "date" | "number" | "image" | "select"
          - required: bool
          - default: str       → valor por defecto (opcional)
          - options: list[str] → solo para type="select"
          - help: str          → texto de ayuda (opcional)
          - placeholder: str   → placeholder del input
        """
        ...

    @classmethod
    @abstractmethod
    def build_pdf(cls, data: dict, numero: str) -> bytes:
        """
        Genera el PDF con los datos del formulario.
        Retorna bytes del PDF.
        """
        ...

    @classmethod
    def new_canvas(cls) -> tuple[canvas.Canvas, io.BytesIO]:
        """Crea un canvas nuevo sobre un buffer en memoria."""
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
        return c, buf

    @classmethod
    def finish(cls, c: canvas.Canvas, buf: io.BytesIO) -> bytes:
        """Finaliza el canvas y retorna los bytes del PDF."""
        c.save()
        buf.seek(0)
        return buf.getvalue()
