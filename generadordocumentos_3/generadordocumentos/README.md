# 🐘 Generador de Documentos Institucionales · PRADNA Seguros

App Streamlit para generar documentos PDF con branding PRADNA desde cualquier puesto del equipo.

## Documentos disponibles
- 📋 **Solicitud de Endoso** — Autorización para aplicar póliza a crédito bancario
- 🏅 **Certificado / Constancia** — Certificados de cobertura, vigencia, vinculación
- 💰 **Cuenta de Cobro** — Cobro de servicios y comisiones con tabla de conceptos
- ✉️ **Comunicado / Carta** — Cartas formales con membrete institucional

## Instalación local
```bash
git clone https://github.com/antigravitydanielarias-prog/generadordocumentos.git
cd generadordocumentos
pip install -r requirements.txt
streamlit run app.py
```

## Deploy en Streamlit Cloud
1. Sube el repo a GitHub (privado recomendado)
2. Ve a share.streamlit.io → New app
3. Selecciona el repo y apunta a `app.py`
4. Deploy ✅

## Agregar nuevo tipo de documento
1. Crea `core/document_types/mi_doc.py` extendiendo `BaseDocument`
2. Define `get_fields()` y `build_pdf()`
3. Regístralo en `core/document_types/__init__.py`
4. Aparece automáticamente en la app

## Logo PRADNA
Coloca el logo en `assets/logo_pradna.png` para que aparezca en los documentos.
Si no existe, se usa un logo vectorial de respaldo.

---
*PRADNA Seguros · Protección que transciende*
