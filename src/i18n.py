"""Internacionalización: diccionario de traducciones ES/EN."""

TEXTS = {
    "es": {
        # App principal
        "app_title": "📊 Analista Financiero Local",
        "app_subtitle": "🤖 *Tu asistente local para **extraer, validar y analizar** estados financieros con IA (Ollama) + cálculo determinista en Python, sin enviar datos a la nube.*",
        
        # Sidebar
        "sidebar_config": "⚙️ Configuración",
        "sidebar_company": "Nombre de la empresa",
        "sidebar_new_analysis": "🆕 Nuevo análisis",
        "sidebar_help": "❓ Ayuda / Cómo usar",
        "sidebar_history": "📜 Historial de análisis",
        "sidebar_manage": "🗂️ Gestionar / eliminar",
        "sidebar_no_history": "Aún no hay análisis guardados.",
        
        # Ayuda
        "help_step1_title": "1. Analizar cifras 📁🔍",
        "help_step1": "Sube un PDF/Excel/CSV y pulsa *Analizar cifras*. Para Excel/CSV se usa extracción determinista (100% precisa). Para PDF se usa IA.",
        "help_step2_title": "2. Moneda 🪙",
        "help_step2": "Selecciona la moneda de los estados financieros. Se aplicará a todo el informe.",
        "help_step3_title": "3. Validación automática ✅",
        "help_step3": "El sistema comprueba que *Activo = Pasivo + Patrimonio*. Si no cuadra, corrige la tabla antes de continuar.",
        "help_step4_title": "4. Ratios y evolución 📊📈",
        "help_step4": "Se calculan en Python puro. Puedes elegir qué ratios graficar.",
        "help_step5_title": "5. Informe 📝",
        "help_step5": "Genera un informe instantáneo con Python o un análisis narrativo con IA.",
        "help_step6_title": "6. Consulta RAG 💬",
        "help_step6": "Pregunta sobre el documento; la IA responde citando fuentes.",
        
        # Upload
        "upload_label": "📁 Sube estados financieros (PDF, Excel o CSV)",
        
        # Botones principales
        "btn_analyze": "1) Analizar cifras 🔍",
        "btn_report_fast": "📄 Informe Rápido (Automático)",
        "btn_report_ai": "🤖 Informe Narrativo con IA",
        "btn_download_ratios": "⬇️ Descargar ratios CSV",
        
        # Spinners
        "spinner_reading": "📖 Leyendo documento...",
        "spinner_extracting_deterministic": "⚙️ Extrayendo cifras con algoritmo determinista (sin IA)...",
        "spinner_extracting_ai": "🧠 El modelo está extrayendo las cifras...",
        "spinner_ai_report": "🧠 La IA está redactando el informe (puede tardar unos minutos)...",
        "spinner_rag_searching": "🔎 Buscando fuentes y redactando con Ollama...",
        "spinner_rag_retrieving": "Recuperando fragmentos del documento...",
        "spinner_rag_generating": "Generando respuesta...",
        "spinner_rag_done": "✅ Respuesta lista",
        
        # Secciones
        "section_cifras": "🔍 Cifras extraídas (revísalas y corrige si hace falta)",
        "section_ratios": "📊 Ratios calculados",
        "section_evolution": "📈 Evolución de los ratios",
        "section_alerts": "⚠️ Alertas detectadas",
        "section_report": "📝 Generación de Informe",
        "section_rag": "💬 Consulta sobre el documento (RAG)",
        
        # Moneda
        "currency_label": "🪙 Moneda de los estados",
        "currency_custom": "Especificar moneda",
        "currency_applied": "🪙 Se aplicará **{currency}** a todos los periodos del informe.",
        "currency_undefined": "sin definir",
        
        # Validación
        "balance_ok": "✅ Los totales del balance cuadran correctamente.",
        "balance_error": "🚨 **Inconsistencias en el balance** (corrige la tabla arriba):\n\n{errors}",
        "balance_error_item": "⚠️ **{period}**: Activo {asset:,.0f} ≠ Pasivo {liab:,.0f} + Patrimonio {equity:,.0f} (dif. {diff:,.0f})",
        
        # Tabla de cifras - Encabezados y campos
        "table_concept_header": "Concepto",
        "field_efectivo": "Efectivo",
        "field_inventarios": "Inventarios",
        "field_activo_corriente": "Activo corriente",
        "field_activo_total": "Activo total",
        "field_pasivo_corriente": "Pasivo corriente",
        "field_pasivo_total": "Pasivo total",
        "field_patrimonio": "Patrimonio",
        "field_ventas": "Ventas",
        "field_costo_ventas": "Costo de ventas",
        "field_utilidad_operativa": "Utilidad operativa",
        "field_depreciacion_amortizacion": "Depreciación y amortización",
        "field_gastos_financieros": "Gastos financieros",
        "field_utilidad_neta": "Utilidad neta",
        
        # Tabla de ratios - Encabezados
        "table_ratio_header": "Ratio",
        "table_period_header": "Periodo",
        "table_value_header": "Valor",
        "table_range_header": "Rango esperado",
        "table_status_header": "Estado",
        
        # Gráficos
        "chart_select_ratios": "Selecciona los ratios a visualizar:",
        "chart_help": "Puedes elegir entre 1 y 9 ratios para comparar",
        "chart_no_selection": "Selecciona al menos un ratio para visualizar.",
        "chart_period": "Periodo",
        "chart_value": "Valor",
        "chart_ref": "Ref: {value}",
        
        # RAG
        "rag_question_label": "Escribe tu pregunta aquí:",
        "rag_submit": "Responder pregunta 💡",
        "rag_warning_empty": "Escribe una pregunta antes de consultar.",
        "rag_sources": "📚 Ver fuentes",
        "rag_no_sources": "No se recuperaron fragmentos del documento.",
        
        # Historial
        "history_dialog_title": "🗂️ Gestionar historial",
        "history_no_items": "No hay análisis guardados.",
        "history_periods": "Moneda: {currency} · Periodos: {periods}",
        "history_load": "📂",
        "history_load_help": "Cargar este análisis",
        "history_delete": "🗑️",
        "history_delete_help": "Eliminar",
        "history_confirm_warning": "¿Eliminar este análisis? Esta acción no se puede deshacer.",
        "history_confirm_yes": "✅ Sí, eliminar",
        "history_confirm_no": "❌ Cancelar",
        
        # Info messages
        "info_fallback": "Formato tabular no reconocible; usando IA como respaldo...",
        "info_download": "⬇️ Descargar informe ({type}).md",
    },
    "en": {
        # App principal
        "app_title": "📊 Local Financial Analyst",
        "app_subtitle": "🤖 *Your local assistant to **extract, validate and analyze** financial statements with AI (Ollama) + deterministic Python calculations, without sending data to the cloud.*",
        
        # Sidebar
        "sidebar_config": "⚙️ Configuration",
        "sidebar_company": "Company name",
        "sidebar_new_analysis": "🆕 New analysis",
        "sidebar_help": "❓ Help / How to use",
        "sidebar_history": "📜 Analysis history",
        "sidebar_manage": "🗂️ Manage / delete",
        "sidebar_no_history": "No saved analyses yet.",
        
        # Ayuda
        "help_step1_title": "1. Analyze figures 📁🔍",
        "help_step1": "Upload a PDF/Excel/CSV and click *Analyze figures*. For Excel/CSV, deterministic extraction is used (100% accurate). For PDF, AI is used.",
        "help_step2_title": "2. Currency 🪙",
        "help_step2": "Select the currency of the financial statements. It will be applied to the entire report.",
        "help_step3_title": "3. Automatic validation ✅",
        "help_step3": "The system checks that *Assets = Liabilities + Equity*. If it doesn't match, correct the table before continuing.",
        "help_step4_title": "4. Ratios and evolution 📊📈",
        "help_step4": "Calculated in pure Python. You can choose which ratios to graph.",
        "help_step5_title": "5. Report 📝",
        "help_step5": "Generate an instant report with Python or a narrative analysis with AI.",
        "help_step6_title": "6. RAG Query 💬",
        "help_step6": "Ask about the document; AI answers citing sources.",
        
        # Upload
        "upload_label": "📁 Upload financial statements (PDF, Excel or CSV)",
        
        # Botones principales
        "btn_analyze": "1) Analyze figures 🔍",
        "btn_report_fast": "📄 Quick Report (Automatic)",
        "btn_report_ai": "🤖 Narrative Report with AI",
        "btn_download_ratios": "⬇️ Download ratios CSV",
        
        # Spinners
        "spinner_reading": "📖 Reading document...",
        "spinner_extracting_deterministic": "⚙️ Extracting figures with deterministic algorithm (no AI)...",
        "spinner_extracting_ai": "🧠 The model is extracting the figures...",
        "spinner_ai_report": "🧠 AI is drafting the report (may take a few minutes)...",
        "spinner_rag_searching": "🔎 Searching sources and drafting with Ollama...",
        "spinner_rag_retrieving": "Retrieving document fragments...",
        "spinner_rag_generating": "Generating response...",
        "spinner_rag_done": "✅ Response ready",
        
        # Secciones
        "section_cifras": "🔍 Extracted figures (review and correct if needed)",
        "section_ratios": "📊 Calculated ratios",
        "section_evolution": "📈 Ratio evolution",
        "section_alerts": "⚠️ Detected alerts",
        "section_report": "📝 Report generation",
        "section_rag": "💬 Document query (RAG)",
        
        # Moneda
        "currency_label": "🪙 Statement currency",
        "currency_custom": "Specify currency",
        "currency_applied": "🪙 **{currency}** will be applied to all report periods.",
        "currency_undefined": "undefined",
        
        # Validación
        "balance_ok": "✅ Balance sheet totals match correctly.",
        "balance_error": "🚨 **Balance sheet inconsistencies** (correct the table above):\n\n{errors}",
        "balance_error_item": "⚠️ **{period}**: Assets {asset:,.0f} ≠ Liabilities {liab:,.0f} + Equity {equity:,.0f} (diff. {diff:,.0f})",
        
        # Tabla de cifras - Encabezados y campos
        "table_concept_header": "Account",
        "field_efectivo": "Cash",
        "field_inventarios": "Inventories",
        "field_activo_corriente": "Current assets",
        "field_activo_total": "Total assets",
        "field_pasivo_corriente": "Current liabilities",
        "field_pasivo_total": "Total liabilities",
        "field_patrimonio": "Equity",
        "field_ventas": "Revenue",
        "field_costo_ventas": "Cost of sales",
        "field_utilidad_operativa": "Operating income",
        "field_depreciacion_amortizacion": "Depreciation & amortization",
        "field_gastos_financieros": "Financial expenses",
        "field_utilidad_neta": "Net income",
        
        # Tabla de ratios - Encabezados
        "table_ratio_header": "Ratio",
        "table_period_header": "Period",
        "table_value_header": "Value",
        "table_range_header": "Expected range",
        "table_status_header": "Status",
        
        # Gráficos
        "chart_select_ratios": "Select ratios to visualize:",
        "chart_help": "You can choose between 1 and 9 ratios to compare",
        "chart_no_selection": "Select at least one ratio to visualize.",
        "chart_period": "Period",
        "chart_value": "Value",
        "chart_ref": "Ref: {value}",
        
        # RAG
        "rag_question_label": "Type your question here:",
        "rag_submit": "Answer question 💡",
        "rag_warning_empty": "Type a question before querying.",
        "rag_sources": "📚 View sources",
        "rag_no_sources": "No document fragments were retrieved.",
        
        # Historial
        "history_dialog_title": "🗂️ Manage history",
        "history_no_items": "No saved analyses.",
        "history_periods": "Currency: {currency} · Periods: {periods}",
        "history_load": "📂",
        "history_load_help": "Load this analysis",
        "history_delete": "🗑️",
        "history_delete_help": "Delete",
        "history_confirm_warning": "Delete this analysis? This action cannot be undone.",
        "history_confirm_yes": "✅ Yes, delete",
        "history_confirm_no": "❌ Cancel",
        
        # Info messages
        "info_fallback": "Tabular format not recognized; using AI as fallback...",
        "info_download": "⬇️ Download report ({type}).md",
    }
}

def get_text(key: str, lang: str = "es", **kwargs) -> str:
    """Retorna el texto traducido. Si no existe la clave, retorna la clave misma."""
    text = TEXTS.get(lang, TEXTS["es"]).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text