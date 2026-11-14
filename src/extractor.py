"""El LLM SOLO extrae cifras a JSON. No calcula nada."""
import json
from langchain_ollama import ChatOllama
from .config import OLLAMA_BASE_URL, LLM_MODEL, NUM_CTX
from .schemas import EstadosFinancieros

PROMPT = """Eres un contador experto. Del siguiente documento extrae las cifras
de los estados financieros para cada periodo que aparezca.

IMPORTANTE: Debes extraer TODOS los campos del schema, incluso si crees que son secundarios.
Si un valor no aparece en el documento, usa null. NUNCA omitas un campo.

Devuelve SOLO un JSON con la forma {{"periodos": [ ... ]}} donde cada elemento
tiene EXACTAMENTE estas claves (no agregues ni quites ninguna):
{campos}

Usa números sin separadores de miles (ej. 1250000.5). Si un dato no aparece usa null.
No inventes valores. Revisa cada fila de cada tabla del documento.

DOCUMENTO:
{doc}
"""

CAMPOS_CRITICOS = [
    "activo_corriente", "activo_total", "pasivo_corriente", "pasivo_total",
    "patrimonio", "ventas", "utilidad_neta", "gastos_financieros"
]

def extraer_estados(texto: str, max_chars: int = 12000) -> list[EstadosFinancieros]:
    llm = ChatOllama(
        model=LLM_MODEL, 
        base_url=OLLAMA_BASE_URL,
        num_ctx=NUM_CTX, 
        temperature=0, 
        format="json"
    )
    campos = ", ".join(EstadosFinancieros.model_fields.keys())
    resp = llm.invoke(PROMPT.format(campos=campos, doc=texto[:max_chars]))
    data = json.loads(resp.content)
    periodos = data.get("periodos", [data]) if isinstance(data, dict) else data
    
    estados = [EstadosFinancieros(**p) for p in periodos]
    
    # Validación: alertar si campos críticos están en null
    for e in estados:
        faltantes = [c for c in CAMPOS_CRITICOS if getattr(e, c) is None]
        if faltantes:
            print(f"⚠️  Periodo {e.periodo}: campos críticos sin extraer: {faltantes}")
    
    return estados