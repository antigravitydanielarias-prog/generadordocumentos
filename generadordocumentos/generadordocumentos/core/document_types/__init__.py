"""Registro de todos los tipos de documento disponibles."""
from core.document_types.endoso      import SolicitudEndoso
from core.document_types.certificado import Certificado
from core.document_types.cuenta_cobro import CuentaCobro
from core.document_types.comunicado  import Comunicado

# Registro global — agregar nuevos tipos aquí
DOCUMENT_TYPES: dict[str, type] = {
    "Solicitud de Endoso":     SolicitudEndoso,
    "Certificado / Constancia": Certificado,
    "Cuenta de Cobro":         CuentaCobro,
    "Comunicado / Carta":      Comunicado,
}
