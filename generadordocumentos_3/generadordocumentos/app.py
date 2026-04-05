"""
app.py — Generador de Documentos Institucionales · PRADNA Seguros
"""
from __future__ import annotations

import io
import uuid
from datetime import date
from pathlib import Path

import streamlit as st

from core.document_types import DOCUMENT_TYPES
from core.pdf_builder import FONTS_DIR, BASE_DIR

# ── Diagnóstico de arranque ──────────────────────────────────────────────────
import sys, pathlib
_issues = []
if not FONTS_DIR.exists():
    _issues.append(f"Carpeta fonts/ no encontrada en: {FONTS_DIR}")
if not (BASE_DIR / "core").exists():
    _issues.append(f"Carpeta core/ no encontrada en: {BASE_DIR}")

# ── CONFIG ────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Generador de Documentos · PRADNA",
    page_icon="🐘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── LOGIN ────────────────────────────────────────────────────────────────────
# Credenciales configurables — en producción usa st.secrets
USERS = {
    "pradna":   "pradna2025",
    "yohanna":  "seguros2025",
    "daniel":   "admin2025",
}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("""
    <div style="max-width:380px;margin:80px auto 0;text-align:center;">
        <div style="background:linear-gradient(135deg,#1A0F30,#341E52);
                    padding:28px 32px 24px;border-radius:16px;margin-bottom:24px;">
            <div style="font-size:1.4rem;font-weight:900;color:#C8A84B;
                        letter-spacing:3px;margin-bottom:4px;">PRADNA</div>
            <div style="font-size:0.7rem;color:rgba(255,255,255,0.4);
                        letter-spacing:2px;text-transform:uppercase;">
                Generador de Documentos</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("**Iniciar sesión**")
            usuario = st.text_input("Usuario", placeholder="tu usuario")
            clave   = st.text_input("Contraseña", type="password", placeholder="••••••••")
            login_btn = st.form_submit_button("Ingresar", use_container_width=True, type="primary")

        if login_btn:
            if usuario in USERS and USERS[usuario] == clave:
                st.session_state["logged_in"] = True
                st.session_state["usuario_actual"] = usuario
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

    st.stop()

# ── DIAGNÓSTICO (solo muestra si hay problemas) ──────────────────────────────
if '_issues' in dir() and _issues:
    for _iss in _issues:
        st.error(f"Error de configuración: {_iss}")
    st.stop()

# ── ESTILOS ───────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Lato', sans-serif !important; }

.main-title {
    font-size: 2rem; font-weight: 900; color: #341E52;
    letter-spacing: -0.5px; margin-bottom: 2px; line-height: 1.1;
}
.doc-type-card {
    background: white; border: 2px solid #E4DCF4;
    border-radius: 14px; padding: 20px 18px;
    cursor: pointer; transition: all .2s;
    text-align: center; height: 100%;
}
.doc-type-card:hover { border-color: #C8A84B; transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(52,30,82,0.12); }
.doc-type-card.selected { border-color: #341E52; background: #F8F4FF; }
.doc-icon { font-size: 2.4rem; margin-bottom: 8px; }
.doc-name { font-size: 0.88rem; font-weight: 700; color: #341E52; margin-bottom: 4px; }
.doc-desc { font-size: 0.72rem; color: #7A6A9A; line-height: 1.4; }

.sec-label {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 2.5px;
    text-transform: uppercase; color: #C8A84B;
    border-left: 3px solid #C8A84B; padding-left: 8px;
    margin: 20px 0 12px;
}
.preview-box {
    background: #F8F4FF; border: 1px solid #E4DCF4;
    border-radius: 12px; padding: 16px;
    font-size: 0.82rem; color: #341E52;
}
.field-help { font-size: 0.72rem; color: #9B8DB0; margin-top: 2px; }

.pradna-header {
    background: linear-gradient(135deg, #1A0F30, #341E52);
    padding: 20px 22px 16px; border-radius: 14px;
    margin-bottom: 18px;
}
.pradna-header .brand { font-size: 1.4rem; font-weight: 900;
    color: #C8A84B; letter-spacing: 3px; }
.pradna-header .sub { font-size: 0.65rem; color: rgba(255,255,255,0.45);
    letter-spacing: 2px; text-transform: uppercase; }

.num-badge {
    background: #EDE8F7; color: #341E52; padding: 3px 10px;
    border-radius: 20px; font-size: 0.78rem; font-weight: 700;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────

if "doc_tipo"    not in st.session_state: st.session_state["doc_tipo"]    = None
if "form_data"   not in st.session_state: st.session_state["form_data"]   = {}
if "pdf_result"  not in st.session_state: st.session_state["pdf_result"]  = None
if "doc_numero"  not in st.session_state: st.session_state["doc_numero"]  = ""
if "historial"   not in st.session_state: st.session_state["historial"]   = []

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="pradna-header">
        <div class="brand">🐘 PRADNA</div>
        <div class="sub">Generador de Documentos</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Documentos disponibles")
    for nombre, cls in DOCUMENT_TYPES.items():
        is_sel = st.session_state["doc_tipo"] == nombre
        bg = "#F0EBF8" if is_sel else "transparent"
        bd = "#341E52" if is_sel else "transparent"
        if st.button(
            f"{cls.icono}  {nombre}",
            key=f"sb_{nombre}",
            use_container_width=True,
            type="primary" if is_sel else "secondary",
        ):
            st.session_state["doc_tipo"]   = nombre
            st.session_state["form_data"]  = {}
            st.session_state["pdf_result"] = None
            st.rerun()

    st.divider()

    # Historial
    if st.session_state["historial"]:
        st.markdown("### 📋 Historial de sesión")
        for h in reversed(st.session_state["historial"][-8:]):
            st.caption(f"`{h['numero']}` — {h['tipo']}")
    else:
        st.caption("Los documentos generados aparecerán aquí.")

    st.divider()
    st.divider()
    usuario_actual = st.session_state.get("usuario_actual","")
    st.caption(f"Usuario: **{usuario_actual}**")
    if st.button("Cerrar sesión", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["usuario_actual"] = ""
        st.rerun()
    st.caption("PRADNA Seguros · Protección que transciende")


# ── MAIN ──────────────────────────────────────────────────────────────────────

# Header
col_t, col_n = st.columns([3, 1])
with col_t:
    tipo_actual = st.session_state["doc_tipo"]
    if tipo_actual:
        cls = DOCUMENT_TYPES[tipo_actual]
        st.markdown(f'<p class="main-title">{cls.icono} {tipo_actual}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#7A6A9A;font-size:0.88rem;">{cls.descripcion}</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="main-title">🐘 Generador de Documentos</p>', unsafe_allow_html=True)
        st.markdown('<p style="color:#7A6A9A;">Selecciona un tipo de documento en el panel izquierdo.</p>', unsafe_allow_html=True)

with col_n:
    if tipo_actual:
        # Número de documento
        if not st.session_state["doc_numero"]:
            year  = date.today().year
            uid   = str(uuid.uuid4())[:4].upper()
            abrev = {
                "Solicitud de Endoso": "END",
                "Certificado / Constancia": "CERT",
                "Cuenta de Cobro": "CC",
                "Comunicado / Carta": "COM",
            }.get(tipo_actual, "DOC")
            st.session_state["doc_numero"] = f"{abrev}-{year}-{uid}"

        new_num = st.text_input("N° documento", value=st.session_state["doc_numero"], label_visibility="collapsed")
        st.session_state["doc_numero"] = new_num
        st.markdown(f'<div class="num-badge">{new_num}</div>', unsafe_allow_html=True)

# ── Selector de tipo si ninguno elegido ───────────────────────────────────────

if not tipo_actual:
    st.markdown('<div class="sec-label">Selecciona el tipo de documento</div>', unsafe_allow_html=True)
    cols = st.columns(len(DOCUMENT_TYPES))
    for i, (nombre, cls) in enumerate(DOCUMENT_TYPES.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="doc-type-card">
                <div class="doc-icon">{cls.icono}</div>
                <div class="doc-name">{nombre}</div>
                <div class="doc-desc">{cls.descripcion}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Seleccionar", key=f"sel_{nombre}", use_container_width=True):
                st.session_state["doc_tipo"]   = nombre
                st.session_state["form_data"]  = {}
                st.session_state["pdf_result"] = None
                st.rerun()
    st.stop()

# ── FORMULARIO ────────────────────────────────────────────────────────────────

cls    = DOCUMENT_TYPES[tipo_actual]
fields = cls.get_fields()

col_form, col_prev = st.columns([1, 1], gap="large")

with col_form:
    st.markdown('<div class="sec-label">Completar información</div>', unsafe_allow_html=True)

    form_data = dict(st.session_state.get("form_data", {}))
    image_data: dict[str, bytes] = {}

    with st.form("doc_form", clear_on_submit=False):
        for field in fields:
            key      = field["key"]
            label    = field["label"]
            ftype    = field["type"]
            required = field.get("required", False)
            default  = form_data.get(key, field.get("default", ""))
            opts     = field.get("options", [])
            help_txt = field.get("help", "")
            placeholder = field.get("placeholder","")
            req_mark = " *" if required else ""

            if ftype == "text":
                val = st.text_input(
                    f"{label}{req_mark}",
                    value=str(default),
                    placeholder=placeholder,
                    help=help_txt,
                    key=f"f_{key}",
                )
                form_data[key] = val

            elif ftype == "textarea":
                val = st.text_area(
                    f"{label}{req_mark}",
                    value=str(default),
                    placeholder=placeholder,
                    help=help_txt,
                    height=140,
                    key=f"f_{key}",
                )
                form_data[key] = val

            elif ftype == "date":
                try:
                    from datetime import datetime
                    def_date = datetime.strptime(str(default), "%Y-%m-%d").date() if default else date.today()
                except Exception:
                    def_date = date.today()
                val = st.date_input(
                    f"{label}{req_mark}",
                    value=def_date,
                    help=help_txt,
                    key=f"f_{key}",
                )
                form_data[key] = str(val)

            elif ftype == "number":
                val = st.text_input(
                    f"{label}{req_mark}",
                    value=str(default),
                    placeholder=placeholder,
                    help=help_txt,
                    key=f"f_{key}",
                )
                form_data[key] = val

            elif ftype == "select":
                idx = opts.index(default) if default in opts else 0
                val = st.selectbox(
                    f"{label}{req_mark}",
                    options=opts,
                    index=idx,
                    help=help_txt,
                    key=f"f_{key}",
                )
                form_data[key] = val

            elif ftype == "image":
                up = st.file_uploader(
                    f"{label}{req_mark}",
                    type=["png","jpg","jpeg"],
                    help=help_txt,
                    key=f"f_{key}",
                )
                if up:
                    image_data[key] = up.read()
                    form_data[key] = f"[imagen subida: {up.name}]"
                    st.image(up, width=160, caption="Vista previa")

        st.markdown("")
        submitted = st.form_submit_button(
            "🚀 Generar PDF",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        # Validar campos requeridos
        missing = [
            f["label"] for f in fields
            if f.get("required") and not form_data.get(f["key"], "").strip()
        ]
        if missing:
            st.error("Campos obligatorios incompletos: " + ", ".join(missing))
        else:
            try:
                with st.spinner("Generando documento..."):
                    numero   = st.session_state["doc_numero"]
                    pdf_data = cls.build_pdf({**form_data, **{k: v for k,v in image_data.items()}}, numero)
                    st.session_state["pdf_result"] = pdf_data
                    st.session_state["form_data"]  = form_data
                    # Guardar en historial
                    st.session_state["historial"].append({
                        "numero": numero,
                        "tipo":   tipo_actual,
                        "fecha":  str(date.today()),
                    })
                    # Generar nuevo número para el siguiente doc
                    year  = date.today().year
                    uid   = str(uuid.uuid4())[:4].upper()
                    abrev = {
                        "Solicitud de Endoso": "END",
                        "Certificado / Constancia": "CERT",
                        "Cuenta de Cobro": "CC",
                        "Comunicado / Carta": "COM",
                    }.get(tipo_actual, "DOC")
                    st.session_state["doc_numero"] = f"{abrev}-{year}-{uid}"
                st.rerun()
            except Exception as e:
                st.error(f"Error al generar el PDF: {e}")
                import traceback; st.code(traceback.format_exc())

# ── PREVIEW / DESCARGA ────────────────────────────────────────────────────────

with col_prev:
    st.markdown('<div class="sec-label">Resultado</div>', unsafe_allow_html=True)

    pdf_result = st.session_state.get("pdf_result")

    if not pdf_result:
        st.markdown("""
        <div class="preview-box" style="text-align:center; padding: 40px 20px; color: #9B8DB0;">
            <div style="font-size:3rem; margin-bottom:12px;">📄</div>
            <div style="font-weight:700; color:#341E52; margin-bottom:6px;">El PDF aparecerá aquí</div>
            <div style="font-size:0.8rem;">Completa el formulario y haz clic en <b>Generar PDF</b></div>
        </div>
        """, unsafe_allow_html=True)

        # Resumen de campos
        form_data = st.session_state.get("form_data", {})
        if form_data:
            st.markdown('<div class="sec-label">Datos ingresados</div>', unsafe_allow_html=True)
            for field in fields:
                key = field["key"]
                val = form_data.get(key, "")
                if val:
                    st.caption(f"**{field['label']}:** {val}")
    else:
        # Descarga
        numero = st.session_state["historial"][-1]["numero"] if st.session_state["historial"] else "documento"
        fname  = f"PRADNA_{tipo_actual.replace(' ','_').replace('/','_')}_{numero}.pdf"

        st.success(f"✅ **{tipo_actual}** generado exitosamente")

        st.download_button(
            label="⬇️ Descargar PDF",
            data=pdf_result,
            file_name=fname,
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )

        # Mostrar preview de campos usados
        st.markdown('<div class="sec-label">Resumen del documento</div>', unsafe_allow_html=True)
        form_data = st.session_state.get("form_data", {})
        for field in fields:
            key = field["key"]
            val = form_data.get(key, "")
            if val and field["type"] != "image":
                st.markdown(
                    f'<div style="margin-bottom:6px;">'
                    f'<span style="font-size:0.68rem;color:#C8A84B;font-weight:700;'
                    f'text-transform:uppercase;letter-spacing:1px;">{field["label"]}</span><br>'
                    f'<span style="font-size:0.88rem;color:#341E52;">{val}</span></div>',
                    unsafe_allow_html=True
                )

        st.markdown("")
        if st.button("🔄 Generar otro documento", use_container_width=True):
            st.session_state["pdf_result"] = None
            st.session_state["form_data"]  = {}
            st.rerun()
