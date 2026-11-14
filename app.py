import altair as alt
import pandas as pd
import streamlit as st
import json
import os
from hashlib import sha256
from datetime import datetime

from src.loaders import leer_archivo
from src.extractor import extraer_estados
from src.tabular_extractor import extraer_tabular
from src.ratios import tabla_ratios, alertas
from src.schemas import EstadosFinancieros
from src import rag
from src.report_generator import generar_informe_determinista
from src.ai_report import generar_informe_ia
from src.i18n import get_text

HISTORIAL_PATH = "historial.json"

st.set_page_config(page_title="Analista Financiero Local", page_icon="📈", layout="wide")

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "lang" not in st.session_state:
    st.session_state.lang = "es"

def t(key, **kwargs):
    return get_text(key, st.session_state.lang, **kwargs)

st.title(t("app_title"))
st.markdown(t("app_subtitle"))

# ---------- Evaluadores de estado de los ratios ----------
def _e_liq(v):
    if v is None: return "➖ N/A"
    if v < 1: return "🔴 Critical" if st.session_state.lang == "en" else "🔴 Crítico"
    if v < 1.5: return "⚠️ Low" if st.session_state.lang == "en" else "⚠️ Bajo"
    if v <= 2.0: return "✅ Optimal" if st.session_state.lang == "en" else "✅ Óptimo"
    return "🔵 High" if st.session_state.lang == "en" else "🔵 Alto"

def _e_acida(v):
    if v is None: return "➖ N/A"
    if v >= 1.0: return "✅ Optimal" if st.session_state.lang == "en" else "✅ Óptimo"
    return "⚠️ Low" if st.session_state.lang == "en" else "⚠️ Bajo"

def _e_end(v):
    if v is None: return "➖ N/A"
    if v <= 0.6: return "✅ Healthy" if st.session_state.lang == "en" else "✅ Saludable"
    if v <= 0.7: return "🔶 Moderate" if st.session_state.lang == "en" else "🔶 Moderado"
    return "🔴 High" if st.session_state.lang == "en" else "🔴 Alto"

def _e_mbruto(v):
    if v is None: return "➖ N/A"
    if v >= 0.3: return "✅ Good" if st.session_state.lang == "en" else "✅ Bueno"
    if v >= 0.15: return "🔶 Regular" if st.session_state.lang == "en" else "🔶 Regular"
    return "🔴 Low" if st.session_state.lang == "en" else "🔴 Bajo"

def _e_mneto(v):
    if v is None: return "➖ N/A"
    if v < 0: return "🔴 Negative" if st.session_state.lang == "en" else "🔴 Negativo"
    if v >= 0.1: return "✅ Good" if st.session_state.lang == "en" else "✅ Bueno"
    return "🔶 Low" if st.session_state.lang == "en" else "🔶 Bajo"

def _e_roe(v):
    if v is None: return "➖ N/A"
    if v >= 0.15: return "✅ Good" if st.session_state.lang == "en" else "✅ Bueno"
    if v >= 0.05: return "🔶 Regular" if st.session_state.lang == "en" else "🔶 Regular"
    return "🔴 Low" if st.session_state.lang == "en" else "🔴 Bajo"

def _e_roa(v):
    if v is None: return "➖ N/A"
    if v >= 0.05: return "✅ Good" if st.session_state.lang == "en" else "✅ Bueno"
    if v >= 0.02: return "🔶 Regular" if st.session_state.lang == "en" else "🔶 Regular"
    return "🔴 Low" if st.session_state.lang == "en" else "🔴 Bajo"

def _e_apal(v):
    if v is None: return "➖ N/A"
    if v <= 2.0: return "✅ Healthy" if st.session_state.lang == "en" else "✅ Saludable"
    if v <= 3.0: return "🔶 Moderate" if st.session_state.lang == "en" else "🔶 Moderado"
    return "🔴 High" if st.session_state.lang == "en" else "🔴 Alto"

def _e_cob(v):
    if v is None: return "➖ N/A"
    if v >= 2.0: return "✅ Strong" if st.session_state.lang == "en" else "✅ Fuerte"
    if v >= 1.5: return "🔶 Acceptable" if st.session_state.lang == "en" else "🔶 Aceptable"
    return "🔴 Weak" if st.session_state.lang == "en" else "🔴 Débil"

RATIOS_META = [
    ("liquidez_corriente", "Current ratio" if st.session_state.lang == "en" else "Liquidez corriente", "1.5 – 2.0", _e_liq),
    ("prueba_acida", "Quick ratio" if st.session_state.lang == "en" else "Prueba ácida", "> 1.0", _e_acida),
    ("endeudamiento", "Debt ratio" if st.session_state.lang == "en" else "Endeudamiento", "< 60%", _e_end),
    ("margen_bruto", "Gross margin" if st.session_state.lang == "en" else "Margen bruto", "> 30%", _e_mbruto),
    ("margen_neto", "Net margin" if st.session_state.lang == "en" else "Margen neto", "> 10%", _e_mneto),
    ("roe", "ROE", "> 15%", _e_roe),
    ("roa", "ROA", "> 5%", _e_roa),
    ("apalancamiento", "Leverage" if st.session_state.lang == "en" else "Apalancamiento", "< 2.0", _e_apal),
    ("cobertura_intereses", "Interest coverage" if st.session_state.lang == "en" else "Cobertura de intereses", "> 1.5", _e_cob),
]

# ---------- Helpers de historial ----------
def _cargar_historial():
    if os.path.exists(HISTORIAL_PATH):
        with open(HISTORIAL_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def _guardar_historial(h):
    with open(HISTORIAL_PATH, "w", encoding="utf-8") as f:
        json.dump(h[-20:], f, indent=2, ensure_ascii=False)

def _cargar_analisis(h):
    st.session_state.estados = h.get("cifras", [])
    st.session_state.documento_id = None
    st.session_state["cargado_desde_historial"] = True
    st.session_state["empresa_hist"] = h.get("empresa", "Mi Empresa C.A.")
    st.session_state.pop("respuesta_rag", None)
    st.session_state.pop("informe_generado", None)
    st.rerun()

# ---------- Sidebar: idioma PRIMERO ----------
with st.sidebar:
    lang_options = {"es": "🇪🇸 Español", "en": "🇺🇸 English"}
    current_lang = st.session_state.get("lang", "es")
    
    lang = st.selectbox(
        "🌐 Language / Idioma",
        options=list(lang_options.keys()),
        format_func=lambda x: lang_options[x],
        index=list(lang_options.keys()).index(current_lang),
        key="lang_selector"
    )
    
    if lang != st.session_state.lang:
        st.session_state.lang = lang
        st.rerun()
    
    st.header(t("sidebar_config"))
    empresa = st.text_input(t("sidebar_company"),
                            st.session_state.get("empresa_hist", "Mi Empresa C.A."))

    st.divider()
    if st.button(t("sidebar_new_analysis"), use_container_width=True):
        for k in ("estados", "respuesta_rag", "documento_id",
                  "cargado_desde_historial", "empresa_hist", "guardar_historial",
                  "informe_generado", "tipo_informe", "moneda_global"):
            st.session_state.pop(k, None)
        st.session_state.uploader_key += 1
        st.rerun()

    with st.expander(t("sidebar_help")):
        st.markdown(
            f"**{t('help_step1_title')}**\n\n"
            f"{t('help_step1')}\n\n"
            f"**{t('help_step2_title')}**\n\n"
            f"{t('help_step2')}\n\n"
            f"**{t('help_step3_title')}**\n\n"
            f"{t('help_step3')}\n\n"
            f"**{t('help_step4_title')}**\n\n"
            f"{t('help_step4')}\n\n"
            f"**{t('help_step5_title')}**\n\n"
            f"{t('help_step5')}\n\n"
            f"**{t('help_step6_title')}**\n\n"
            f"{t('help_step6')}"
        )

# ---------- Carga de archivo ----------
archivo = st.file_uploader(
    t("upload_label"),
    type=["pdf", "xlsx", "xls", "csv"],
    key=f"uploader_{st.session_state.uploader_key}"
)
documento_id = (archivo.name, sha256(archivo.getvalue()).hexdigest()) if archivo else None

if archivo is None and st.session_state.get("documento_id") is not None:
    for clave in ("estados", "respuesta_rag", "documento_id"):
        st.session_state.pop(clave, None)
    st.session_state.pop("cargado_desde_historial", None)
elif documento_id is not None and st.session_state.get("documento_id") != documento_id:
    for clave in ("estados", "respuesta_rag", "informe_generado", "tipo_informe"):
        st.session_state.pop(clave, None)
    st.session_state.documento_id = documento_id
    st.session_state.pop("cargado_desde_historial", None)

# ---------- Botón 1: Analizar ----------
analizar = st.button(t("btn_analyze"), type="primary", disabled=not archivo)
if analizar:
    for clave in ("estados", "respuesta_rag", "informe_generado", "tipo_informe"):
        st.session_state.pop(clave, None)
    
    data = archivo.getvalue()
    with st.spinner(t("spinner_reading")):
        texto = leer_archivo(data, archivo.name)
        rag.indexar(texto, archivo.name)

    es_tabular = archivo.name.lower().endswith((".csv", ".xlsx", ".xls"))
    estados_extraidos = []
    
    if es_tabular:
        with st.spinner(t("spinner_extracting_deterministic")):
            estados_extraidos = extraer_tabular(data, archivo.name)

    if estados_extraidos:
        st.session_state.estados = [e.model_dump() for e in estados_extraidos]
    else:
        if es_tabular:
            st.info(t("info_fallback"))
        with st.spinner(t("spinner_extracting_ai")):
            st.session_state.estados = [e.model_dump() for e in extraer_estados(texto)]
            
    st.session_state["guardar_historial"] = True

# ---------- Visualización + validación ----------
if "estados" in st.session_state:
    st.subheader(t("section_cifras"))
    df_wide = pd.DataFrame(st.session_state.estados)

    # ========== 🪙 MONEDA ==========
    MONEDAS = ["Bs", "USD", "EUR", "COP", "MXN", "ARS", "CLP", "PEN", "Otra"]
    moneda_detectada = next(
        (e.get("moneda") for e in st.session_state.estados if e.get("moneda")),
        None
    )
    
    col_m1, col_m2 = st.columns([1, 3])
    with col_m1:
        idx = MONEDAS.index(moneda_detectada) if moneda_detectada in MONEDAS else 0
        sel = st.selectbox(t("currency_label"), MONEDAS, index=idx, key="sel_moneda")
    with col_m2:
        if sel == "Otra":
            moneda = st.text_input(t("currency_custom"), 
                                   value=moneda_detectada or "", 
                                   key="moneda_custom", 
                                   label_visibility="collapsed")
        else:
            moneda = sel
            
    st.session_state["moneda_global"] = moneda
    st.caption(t("currency_applied", currency=moneda or t("currency_undefined")))

    # Tabla SIN la fila 'moneda'
    df_cifras = df_wide.set_index("periodo").T.reset_index().rename(columns={"index": "Concepto"})
    df_cifras = df_cifras[df_cifras["Concepto"] != "moneda"]
    
    # ✅ Traducir nombres de campos
    field_translations = {
        "efectivo": t("field_efectivo"),
        "inventarios": t("field_inventarios"),
        "activo_corriente": t("field_activo_corriente"),
        "activo_total": t("field_activo_total"),
        "pasivo_corriente": t("field_pasivo_corriente"),
        "pasivo_total": t("field_pasivo_total"),
        "patrimonio": t("field_patrimonio"),
        "ventas": t("field_ventas"),
        "costo_ventas": t("field_costo_ventas"),
        "utilidad_operativa": t("field_utilidad_operativa"),
        "depreciacion_amortizacion": t("field_depreciacion_amortizacion"),
        "gastos_financieros": t("field_gastos_financieros"),
        "utilidad_neta": t("field_utilidad_neta"),
    }
    df_cifras["Concepto"] = df_cifras["Concepto"].map(
        lambda x: field_translations.get(x, x)
    )
    df_cifras = df_cifras.rename(columns={"Concepto": t("table_concept_header")})

    col_config = {}
    for col in df_cifras.columns:
        if col != t("table_concept_header"):
            col_config[col] = st.column_config.NumberColumn(
                format="%,.2f", step=1, help=f"Cifras del periodo {col}"
            )

    editado = st.data_editor(
        df_cifras, num_rows="fixed", width="stretch",
        key="editor_cifras", column_config=col_config, hide_index=True
    )

    valid_fields = set(EstadosFinancieros.model_fields.keys())
    estados = []
    periodos_cols = [c for c in editado.columns if c != t("table_concept_header")]
    
    # Mapeo inverso para reconstruir los objetos
    reverse_field_map = {v: k for k, v in field_translations.items()}
    
    for periodo in periodos_cols:
        row = {"periodo": str(periodo), "moneda": moneda or None}
        for _, fila in editado.iterrows():
            field_label = fila[t("table_concept_header")]
            field = reverse_field_map.get(field_label, field_label)
            if field in valid_fields and field != "moneda":
                val = fila[periodo]
                row[field] = None if pd.isna(val) else float(val)
        estados.append(EstadosFinancieros(**row))

    errores_balance = []
    for e in estados:
        if e.activo_total and e.pasivo_total and e.patrimonio:
            diff = abs(e.activo_total - (e.pasivo_total + e.patrimonio))
            if diff > e.activo_total * 0.01:
                errores_balance.append(
                    t("balance_error_item", period=e.periodo, asset=e.activo_total, 
                      liab=e.pasivo_total, equity=e.patrimonio, diff=diff))
    
    if errores_balance:
        st.error(t("balance_error", errors="\n\n".join(errores_balance)))
    else:
        st.success(t("balance_ok"))

    df_base = tabla_ratios(estados)
    filas = []
    for _, r in df_base.iterrows():
        for campo, label, rango, fn in RATIOS_META:
            v = r.get(campo)
            v = None if v is None or pd.isna(v) else float(v)
            filas.append({"Ratio": label, "Periodo": str(r["periodo"]),
                          "Valor": None if v is None else round(v, 4),
                          "Rango esperado": rango, "Estado": fn(v)})
    df_ratios = pd.DataFrame(filas)
    
    # ✅ Traducir encabezados de la tabla de ratios
    df_ratios = df_ratios.rename(columns={
        "Ratio": t("table_ratio_header"),
        "Periodo": t("table_period_header"),
        "Valor": t("table_value_header"),
        "Rango esperado": t("table_range_header"),
        "Estado": t("table_status_header"),
    })

    st.subheader(t("section_ratios"))
    st.dataframe(df_ratios, width="stretch", hide_index=True)

    # ---------- Gráficos de evolución con selector ----------
    st.subheader(t("section_evolution"))
    todos_ratios = {
        "liquidez_corriente": "Current Ratio" if st.session_state.lang == "en" else "Liquidez Corriente",
        "prueba_acida": "Quick Ratio" if st.session_state.lang == "en" else "Prueba Ácida",
        "endeudamiento": "Debt Ratio" if st.session_state.lang == "en" else "Endeudamiento",
        "apalancamiento": "Leverage" if st.session_state.lang == "en" else "Apalancamiento",
        "margen_bruto": "Gross Margin" if st.session_state.lang == "en" else "Margen Bruto",
        "margen_neto": "Net Margin" if st.session_state.lang == "en" else "Margen Neto",
        "roe": "ROE",
        "roa": "ROA",
        "cobertura_intereses": "Interest Coverage" if st.session_state.lang == "en" else "Cobertura de Intereses"
    }

    default_ratios = [
        "Current Ratio" if st.session_state.lang == "en" else "Liquidez Corriente",
        "Debt Ratio" if st.session_state.lang == "en" else "Endeudamiento",
        "Net Margin" if st.session_state.lang == "en" else "Margen Neto",
        "ROE"
    ]

    ratios_seleccionados = st.multiselect(
        t("chart_select_ratios"),
        options=list(todos_ratios.values()),
        default=default_ratios,
        help=t("chart_help")
    )

    if not ratios_seleccionados:
        st.info(t("chart_no_selection"))
    else:
        nombres = {k: v for k, v in todos_ratios.items() if v in ratios_seleccionados}
        rangos_ref = {
            "Liquidez Corriente": 1.75, "Prueba Ácida": 1.0, "Endeudamiento": 0.60,
            "Apalancamiento": 2.0, "Margen Bruto": 0.30, "Margen Neto": 0.10,
            "ROE": 0.15, "ROA": 0.05, "Cobertura de Intereses": 1.5,
            "Current Ratio": 1.75, "Quick Ratio": 1.0, "Debt Ratio": 0.60,
            "Leverage": 2.0, "Gross Margin": 0.30, "Net Margin": 0.10,
            "Interest Coverage": 1.5
        }

        largo = (df_base.assign(periodo=df_base["periodo"].astype(str))
                 .melt(id_vars="periodo", value_vars=list(nombres.keys()),
                       var_name="ratio", value_name="valor"))
        largo["ratio"] = largo["ratio"].map(nombres)

        cols = st.columns(2)
        for i, nombre in enumerate(nombres.values()):
            datos = largo[largo["ratio"] == nombre].dropna(subset=["valor"])
            if datos.empty:
                continue

            ref_val = rangos_ref.get(nombre, 0)
            ref = pd.DataFrame({
                "periodo": datos["periodo"].unique().tolist(),
                "ratio": nombre,
                "valor": [ref_val] * len(datos["periodo"].unique())
            })

            base_chart = alt.Chart(datos).properties(height=260, title=alt.Title(
                text=nombre, fontSize=14, anchor="middle", font="sans-serif"
            ))

            area = base_chart.mark_area(opacity=0.15, color="#2563eb").encode(
                x=alt.X("periodo:O", title=t("chart_period"), axis=alt.Axis(labelAngle=0, labelFontSize=11)),
                y=alt.Y("valor:Q", title=None, scale=alt.Scale(zero=False, padding=20)),
            )
            line = base_chart.mark_line(interpolate="monotone", strokeWidth=3, color="#2563eb").encode(
                x=alt.X("periodo:O", title=t("chart_period"), axis=alt.Axis(labelAngle=0, labelFontSize=11)),
                y=alt.Y("valor:Q", title=None, scale=alt.Scale(zero=False, padding=20)),
            )
            points = base_chart.mark_point(size=100, filled=True, color="#2563eb",
                                           stroke="white", strokeWidth=2).encode(
                x=alt.X("periodo:O", title=t("chart_period")),
                y=alt.Y("valor:Q"),
                tooltip=[alt.Tooltip("periodo:O", title=t("chart_period")),
                         alt.Tooltip("valor:Q", title=t("chart_value"), format=".2%")]
            )
            ref_line = alt.Chart(ref).mark_rule(strokeDash=[6, 4], color="#f59e0b",
                                                strokeWidth=2, opacity=0.8).encode(
                x="periodo:O",
                y=alt.Y("valor:Q", title=None, scale=alt.Scale(zero=False, padding=20)),
            )
            ref_label = alt.Chart(ref.head(1)).mark_text(align="left", baseline="bottom",
                                                         color="#f59e0b", fontSize=10, dx=5).encode(
                x=alt.value(5),
                y=alt.Y("valor:Q", scale=alt.Scale(zero=False, padding=20)),
                text=alt.value(t("chart_ref", value=f"{ref_val:.0%}"))
            )

            chart = (area + line + points + ref_line + ref_label).resolve_scale(y="shared").configure_view(
                strokeWidth=0
            ).configure_axis(grid=True, gridColor="#e5e7eb", gridOpacity=0.5)

            cols[i % 2].altair_chart(chart, width="stretch")

    al = alertas(df_base)
    if al:
        st.subheader(t("section_alerts"))
        for a in al:
            st.warning(a)
    st.download_button(t("btn_download_ratios"), df_ratios.to_csv(index=False), "ratios.csv")

    # ---------- Generación de Informe ----------
    st.divider()
    st.subheader(t("section_report"))
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(t("btn_report_fast"), type="primary", width="stretch"):
            informe = generar_informe_determinista(df_base, al, empresa, moneda)
            st.session_state["informe_generado"] = informe
            st.session_state["tipo_informe"] = "rapido"
    
    with col2:
        if st.button(t("btn_report_ai"), type="secondary", width="stretch"):
            with st.spinner(t("spinner_ai_report")):
                informe = generar_informe_ia(df_base, al, empresa)
            st.session_state["informe_generado"] = informe
            st.session_state["tipo_informe"] = "ia"
    
    if "informe_generado" in st.session_state:
        st.divider()
        st.markdown(st.session_state["informe_generado"])
        tipo = st.session_state.get("tipo_informe", "rapido")
        st.download_button(
            t("info_download", type=tipo),
            st.session_state["informe_generado"],
            f"informe_{empresa.replace(' ', '_')}_{tipo}.md"
        )

    # ---------- Consulta RAG ----------
    st.divider()
    tabla_md = df_base.to_markdown(index=False)
    with st.form("consulta_rag"):
        st.markdown(f"##### {t('section_rag')}")
        pregunta = st.text_input(t("rag_question_label"), key="pregunta_rag")
        consultar = st.form_submit_button(t("rag_submit"), type="secondary")
        
    if consultar:
        st.session_state.pop("respuesta_rag", None)
        if not pregunta.strip():
            st.warning(t("rag_warning_empty"))
        else:
            with st.status(t("spinner_rag_searching"), expanded=True) as status:
                st.write(t("spinner_rag_retrieving"))
                resultado = rag.responder(pregunta, tabla_md)
                st.write(t("spinner_rag_generating"))
                status.update(label=t("spinner_rag_done"), state="complete", expanded=False)
            st.session_state.respuesta_rag = (tabla_md, resultado)
            
    guardada = st.session_state.get("respuesta_rag")
    if guardada and guardada[0] == tabla_md:
        resultado = guardada[1]
        st.markdown(resultado.respuesta)
        with st.expander(t("rag_sources")):
            st.text(resultado.fuentes or t("rag_no_sources"))

    if st.session_state.pop("guardar_historial", False):
        h = _cargar_historial()
        h.append({
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "empresa": empresa,
            "moneda": moneda,
            "periodos": [e.periodo for e in estados],
            "alertas_count": len(al),
            "cifras": st.session_state.estados,
        })
        _guardar_historial(h)

# ---------- Sidebar: historial ----------
@st.dialog(t("history_dialog_title"))
def dialog_historial():
    h = _cargar_historial()
    if not h:
        st.info(t("history_no_items"))
        return
    for i in reversed(range(len(h))):
        item = h[i]
        c1, c2, c3 = st.columns([4, 1, 1], gap="small")
        c1.markdown(f"**📅 {item.get('fecha','N/A')}** · {item.get('empresa','Empresa')}")
        c1.caption(t("history_periods", 
                     currency=item.get('moneda', 'N/A'), 
                     periods=', '.join(item.get('periodos', []))))
        if c2.button(t("history_load"), key=f"ld_{i}", help=t("history_load_help"), use_container_width=True):
            _cargar_analisis(item)
        if c3.button(t("history_delete"), key=f"le_{i}", help=t("history_delete_help"), use_container_width=True):
            st.session_state["hist_confirm"] = i
        if st.session_state.get("hist_confirm") == i:
            st.warning(t("history_confirm_warning"))
            cc1, cc2 = st.columns(2)
            if cc1.button(t("history_confirm_yes"), key=f"yes_{i}"):
                h.pop(i)
                _guardar_historial(h)
                st.session_state.pop("hist_confirm", None)
                st.rerun()
            if cc2.button(t("history_confirm_no"), key=f"no_{i}"):
                st.session_state.pop("hist_confirm", None)
                st.rerun()

with st.sidebar:
    st.divider()
    st.header(t("sidebar_history"))
    historial = _cargar_historial()
    if historial:
        for i in reversed(range(len(historial))):
            item = historial[i]
            if st.button(f"📅 {item.get('fecha','N/A')} · {item.get('empresa','Empresa')}",
                         key=f"hist_{i}", use_container_width=True):
                _cargar_analisis(item)
        st.button(t("sidebar_manage"), on_click=dialog_historial,
                  use_container_width=True)
    else:
        st.info(t("sidebar_no_history"))