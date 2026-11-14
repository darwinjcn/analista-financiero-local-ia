"""Generador de informes financieros determinista (sin LLM)."""
import pandas as pd
from datetime import datetime

def generar_informe_determinista(df_ratios: pd.DataFrame, alertas: list[str], empresa: str, moneda: str = None) -> str:
    """
    Genera un informe Markdown estructurado basado en reglas de negocio.
    df_ratios: DataFrame en formato 'wide' (una fila por periodo) proveniente de tabla_ratios().
    moneda: moneda de los estados financieros (ej. "Bs", "USD").
    """
    periodos = df_ratios["periodo"].astype(str).tolist()
    ultimo = df_ratios.iloc[-1]
    penultimo = df_ratios.iloc[-2] if len(df_ratios) > 1 else None
    
    informe = []
    
    # 1. Encabezado
    informe.append(f"# 📊 Informe de Análisis Financiero: {empresa}")
    informe.append(f"**Fecha de generación:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    informe.append(f"**Moneda:** {moneda or 'No definida'}")
    informe.append(f"**Periodos analizados:** {', '.join(periodos)}\n")
    informe.append("---\n")
    
    # 2. Resumen Ejecutivo
    criticas = [a for a in alertas if "Riesgo" in a or "pérdida" in a or "baja" in a]
    informe.append("## 📌 Resumen Ejecutivo")
    if not alertas:
        informe.append("La empresa presenta una situación financiera **estable y saludable** en todos los indicadores evaluados.\n")
    else:
        informe.append(f"Se detectaron **{len(alertas)} alertas** durante el análisis, de las cuales **{len(criticas)} son críticas**.\n")
        informe.append("A continuación se detalla el análisis por áreas:\n")
    
    # Función auxiliar para formatear porcentajes y decimales
    def fmt(val, is_pct=False):
        if val is None or pd.isna(val): return "N/A"
        return f"{val:.1%}" if is_pct else f"{val:.2f}"

    # 3. Análisis de Liquidez
    informe.append("## 💧 1. Análisis de Liquidez")
    lc = ultimo.get("liquidez_corriente")
    pa = ultimo.get("prueba_acida")
    
    informe.append(f"Al cierre del periodo **{ultimo['periodo']}**, la empresa presenta:")
    informe.append(f"- **Liquidez Corriente:** {fmt(lc)} (Ideal: 1.5 - 2.0)")
    informe.append(f"- **Prueba Ácida:** {fmt(pa)} (Ideal: > 1.0)\n")
    
    if lc is not None:
        if lc < 1:
            informe.append("⚠️ **Diagnóstico:** La empresa tiene más deudas a corto plazo que activos para cubrirlas. Existe un **riesgo inminente de iliquidez**.")
        elif lc < 1.5:
            informe.append("🔶 **Diagnóstico:** La liquidez es ajustada. Se recomienda mejorar la gestión de cobros o renegociar pasivos a corto plazo.")
        elif lc > 2.5:
            informe.append("🔵 **Diagnóstico:** Exceso de liquidez. Podría haber recursos ociosos que no están siendo rentabilizados.")
        else:
            informe.append("✅ **Diagnóstico:** Nivel de liquidez óptimo para cubrir obligaciones a corto plazo.")
    informe.append("")

    # 4. Análisis de Endeudamiento y Solvencia
    informe.append("## 🏦 2. Análisis de Endeudamiento y Solvencia")
    end = ultimo.get("endeudamiento")
    apal = ultimo.get("apalancamiento")
    
    informe.append(f"- **Nivel de Endeudamiento:** {fmt(end, is_pct=True)} (Ideal: < 60%)")
    informe.append(f"- **Apalancamiento Financiero:** {fmt(apal)} (Ideal: < 2.0)\n")
    
    if end is not None:
        if end > 0.7:
            informe.append("🔴 **Diagnóstico:** La empresa está altamente apalancada. Más del 70% de los activos son financiados por terceros, lo que eleva el riesgo financiero.")
        elif end > 0.6:
            informe.append("🔶 **Diagnóstico:** Endeudamiento moderado. Se recomienda monitorear el flujo de caja para asegurar el pago de intereses.")
        else:
            informe.append("✅ **Diagnóstico:** Estructura de capital saludable, con baja dependencia de capital externo.")
    informe.append("")

    # 5. Análisis de Rentabilidad
    informe.append("## 📈 3. Análisis de Rentabilidad")
    mn = ultimo.get("margen_neto")
    roe = ultimo.get("roe")
    roa = ultimo.get("roa")
    
    informe.append(f"- **Margen Neto:** {fmt(mn, is_pct=True)} (Ideal: > 10%)")
    informe.append(f"- **ROE (Retorno sobre Patrimonio):** {fmt(roe, is_pct=True)} (Ideal: > 15%)")
    informe.append(f"- **ROA (Retorno sobre Activos):** {fmt(roa, is_pct=True)} (Ideal: > 5%)\n")
    
    if mn is not None:
        if mn < 0:
            informe.append("🔴 **Diagnóstico:** La empresa está operando con **pérdidas netas**. Es urgente revisar la estructura de costos y precios.")
        elif mn < 0.10:
            informe.append("🔶 **Diagnóstico:** La rentabilidad es baja. Los márgenes no son suficientes para generar un colchón financiero robusto.")
        else:
            informe.append("✅ **Diagnóstico:** La empresa es altamente rentable y genera valor eficientemente.")
    informe.append("")

    # 6. Análisis de Tendencia (si hay más de un periodo)
    if penultimo is not None:
        informe.append("## 📉 4. Análisis de Tendencia (Evolución)")
        lc_prev = penultimo.get("liquidez_corriente")
        lc_curr = ultimo.get("liquidez_corriente")
        if lc_prev and lc_curr:
            diff = lc_curr - lc_prev
            tendencia = "mejoró" if diff > 0 else "empeoró"
            informe.append(f"- La liquidez corriente **{tendencia}** en {abs(diff):.2f} puntos respecto al periodo anterior ({ultimo['periodo']} vs {penultimo['periodo']}).\n")

    # 7. Conclusiones y Recomendaciones
    informe.append("---")
    informe.append("## 🎯 Conclusiones y Recomendaciones")
    if alertas:
        informe.append("Basado en las alertas detectadas, se sugieren las siguientes acciones correctivas:\n")
        for i, alerta in enumerate(alertas, 1):
            texto_limpio = alerta.split(":")[-1].strip().rstrip(".")
            informe.append(f"{i}. **{texto_limpio.capitalize()}.**")
    else:
        informe.append("No se requieren acciones correctivas inmediatas. Se recomienda mantener las políticas financieras actuales.\n")
        
    informe.append("\n---")
    informe.append("*Informe generado automáticamente por Analista Financiero Local (Motor de Reglas de Negocio).*")
    
    return "\n".join(informe)