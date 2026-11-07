"""El LLM SOLO extrae cifras a JSON. No calcula nada."""
import json
from langchain_ollama import ChatOllama
from .config import OLLAMA_BASE_URL, LLM_MODEL, NUM_CTX
from .schemas import EstadosFinancieros

PROMPT = """Eres un contador experto. Del siguiente documento extrae las cifras
de los estados financieros para cada periodo que aparezca.
Devuelve SOLO un JSON con la forma {{"periodos": [ ... ]}} donde cada elemento
tiene estas claves: {campos}.
Usa números sin separadores de miles (ej. 1250000.5). Si un dato no aparece usa null.
No inventes valores.

DOCUMENTO:
{doc}
"""


def extraer_estados(texto: str, max_chars: int = 12000) -> list[EstadosFinancieros]:
    llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL,
                     num_ctx=NUM_CTX, temperature=0, format="json")
    campos = ", ".join(EstadosFinancieros.model_fields.keys())
    resp = llm.invoke(PROMPT.format(campos=campos, doc=texto[:max_chars]))
    data = json.loads(resp.content)
    periodos = data.get("periodos", [data]) if isinstance(data, dict) else data
    return [EstadosFinancieros(**p) for p in periodos]
