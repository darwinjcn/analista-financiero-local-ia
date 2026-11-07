import altair as alt
import pandas as pd
import streamlit as st
from hashlib import sha256
from src.loaders import leer_archivo
from src.extractor import extraer_estados
from src.ratios import tabla_ratios, alertas
from src.schemas import EstadosFinancieros
from src import rag
from src.crew import generar_informe

st.set_page_config(page_title="Analista Financiero Local", layout="wide")
st.title("📊 Analista Financiero Local (Ollama + CrewAI)")

empresa = st.text_input("Nombre de la empresa", "Mi Empresa C.A.")
archivo = st.file_uploader("Sube estados financieros (PDF, Excel o CSV)", type=["pdf", "xlsx", "xls", "csv"])

documento_id = (archivo.name, sha256(archivo.getvalue()).hexdigest()) if archivo else None
if st.session_state.get("documento_id") != documento_id:
    for clave in ("estados", "respuesta_rag", "pregunta_rag"):
        st.session_state.pop(clave, None)
    st.session_state.documento_id = documento_id

if archivo and st.button("1) Extraer cifras"):
    for clave in ("estados", "respuesta_rag"):
        st.session_state.pop(clave, None)
    data = archivo.getvalue()
    with st.spinner("Leyendo documento..."):
        texto = leer_archivo(data, archivo.name)
        rag.indexar(texto, archivo.name)
    with st.spinner("El modelo está extrayendo las cifras..."):
        st.session_state.estados = [e.model_dump() for e in extraer_estados(texto)]

if "estados" in st.session_state:
    st.subheader("Cifras extraídas (revísalas y corrige si hace falta)")
    editado = st.data_editor(pd.DataFrame(st.session_state.estados), num_rows="dynamic")
    estados = [EstadosFinancieros(**{k: (None if pd.isna(v) else v) for k, v in r.items()})
               for r in editado.to_dict("records")]
    df = tabla_ratios(estados)
    st.subheader("Ratios")
    st.dataframe(df, use_container_width=True)
    st.subheader("Evolución de los ratios")
    nombres = {"liquidez_corriente": "Liquidez corriente", "endeudamiento": "Endeudamiento",
               "margen_neto": "Margen neto", "roe": "ROE"}
    largo = (df.assign(periodo=df["periodo"].astype(str))
               .melt(id_vars="periodo", value_vars=list(nombres), var_name="ratio", value_name="valor"))
    largo["ratio"] = largo["ratio"].map(nombres)
    cols = st.columns(2)
    for i, nombre in enumerate(nombres.values()):
        datos = largo[largo["ratio"] == nombre]
        graf = (alt.Chart(datos, title=nombre)
                .mark_line(interpolate="monotone", point=alt.OverlayMarkDef(size=70), strokeWidth=3)
                .encode(x=alt.X("periodo:O", title="Periodo", axis=alt.Axis(labelAngle=0)),
                        y=alt.Y("valor:Q", title=None, scale=alt.Scale(zero=False)),
                        tooltip=["periodo", alt.Tooltip("valor:Q", format=".2f")])
                .properties(height=260))
        cols[i % 2].altair_chart(graf, use_container_width=True)
    al = alertas(df)
    for a in al:
        st.warning(a)
    st.download_button("Descargar ratios CSV", df.to_csv(index=False), "ratios.csv")

    if st.button("2) Generar informe con agentes"):
        with st.spinner("Los agentes están analizando (puede tardar unos minutos en CPU)..."):
            informe = generar_informe(df.to_markdown(index=False), al, empresa)
        st.markdown(informe)
        st.download_button("Descargar informe .md", informe, "informe.md")

    st.divider()
    tabla_md = df.to_markdown(index=False)
    with st.form("consulta_rag"):
        pregunta = st.text_input("Pregunta sobre el documento (RAG)", key="pregunta_rag")
        consultar = st.form_submit_button("Responder pregunta")
    if consultar:
        st.session_state.pop("respuesta_rag", None)
        if not pregunta.strip():
            st.warning("Escribe una pregunta antes de consultar.")
        else:
            try:
                with st.spinner("Buscando fuentes y redactando la respuesta con Ollama..."):
                    resultado = rag.responder(pregunta, tabla_md)
                st.session_state.respuesta_rag = (tabla_md, resultado)
            except Exception as exc:
                st.error(f"No se pudo responder. Comprueba que Ollama esté activo y que ambos modelos estén descargados. Detalle: {exc}")
    guardada = st.session_state.get("respuesta_rag")
    if guardada and guardada[0] == tabla_md:
        resultado = guardada[1]
        st.markdown(resultado.respuesta)
        with st.expander("Ver fuentes"):
            st.text(resultado.fuentes or "No se recuperaron fragmentos del documento.")
            st.markdown("**Ratios calculados a partir de las cifras revisadas**")
            st.dataframe(df, use_container_width=True)
