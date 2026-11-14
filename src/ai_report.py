# src/ai_report.py
"""Generación de informe financiero con Ollama (alternativa al determinista)."""
from langchain_ollama import ChatOllama
from .config import OLLAMA_BASE_URL, LLM_MODEL, NUM_CTX
import pandas as pd

PROMPT_INFORME = """Eres un analista financiero experto. Genera un informe profesional y detallado en español basado en los siguientes datos:

EMPRESA: {empresa}

RATIOS FINANCIEROS:
{ratios}

ALERTAS DETECTADAS:
{alertas}

Estructura el informe así:
1. **Resumen Ejecutivo** (2-3 párrafos sobre la situación general)
2. **Análisis de Liquidez** (interpreta los ratios de liquidez)
3. **Análisis de Endeudamiento** (interpreta endeudamiento y apalancamiento)
4. **Análisis de Rentabilidad** (interpreta márgenes, ROE, ROA)
5. **Conclusiones y Recomendaciones** (basadas en las alertas)

Sé profesional, usa datos concretos de los ratios, y da recomendaciones accionables.
"""

def generar_informe_ia(df_ratios: pd.DataFrame, alertas: list[str], empresa: str) -> str:
    """Genera informe usando Ollama directamente (sin CrewAI)."""
    modelo = ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.3,
        num_ctx=NUM_CTX
    )
    
    # Formatear ratios como tabla legible
    ratios_md = df_ratios.to_markdown(index=False)
    alertas_texto = "\n".join(f"- {a}" for a in alertas) if alertas else "No se detectaron alertas críticas."
    
    prompt = PROMPT_INFORME.format(
        empresa=empresa,
        ratios=ratios_md,
        alertas=alertas_texto
    )
    
    respuesta = modelo.invoke(prompt)
    return respuesta.content