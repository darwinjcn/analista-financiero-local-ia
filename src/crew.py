"""Crew de 2 agentes: Analista (interpreta ratios + RAG) y Redactor (informe ejecutivo)."""
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from .config import OLLAMA_BASE_URL, LLM_MODEL
from . import rag


@tool("buscar_en_documento")
def buscar_en_documento(pregunta: str) -> str:
    """Busca fragmentos relevantes en los estados financieros cargados (notas, contexto)."""
    return rag.buscar(pregunta)


def _llm():
    # Las versiones nuevas de CrewAI hablan con Ollama por su API compatible con OpenAI,
    # que no acepta `num_ctx`. El contexto se fija con OLLAMA_CONTEXT_LENGTH (ver README).
    return LLM(model=f"ollama/{LLM_MODEL}", base_url=OLLAMA_BASE_URL, temperature=0.2)


def generar_informe(tabla_md: str, alertas: list[str], empresa: str) -> str:
    llm = _llm()
    analista = Agent(
        role="Analista financiero senior",
        goal="Interpretar ratios y tendencias sin recalcular cifras",
        backstory="CFA con 15 años analizando estados financieros. Nunca inventa números.",
        tools=[buscar_en_documento], llm=llm, verbose=True, max_iter=4,
    )
    redactor = Agent(
        role="Redactor de informes ejecutivos",
        goal="Convertir el análisis en un informe claro para gerencia",
        backstory="Comunica hallazgos financieros en lenguaje simple y directo.",
        llm=llm, verbose=True,
    )
    t1 = Task(
        description=(f"Empresa: {empresa}.\nRatios calculados (fuente de verdad):\n{tabla_md}\n\n"
                     f"Alertas automáticas:\n" + "\n".join(alertas or ["Ninguna"]) +
                     "\n\nAnaliza liquidez, solvencia, rentabilidad y tendencia entre periodos. "
                     "Usa la herramienta para buscar explicaciones en las notas si hace falta."),
        expected_output="Análisis por área con fortalezas, debilidades y riesgos.",
        agent=analista,
    )
    t2 = Task(
        description="Redacta un informe ejecutivo en Markdown en español: resumen, hallazgos clave, riesgos y 3 recomendaciones.",
        expected_output="Informe en Markdown de máximo 500 palabras.",
        agent=redactor, context=[t1],
    )
    crew = Crew(agents=[analista, redactor], tasks=[t1, t2], process=Process.sequential)
    return str(crew.kickoff())
