from types import SimpleNamespace

import pytest
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from src import rag


class EmbeddingsSimulados(Embeddings):
    def embed_documents(self, texts):
        return [[float(len(text)), 1.0, 0.0] for text in texts]

    def embed_query(self, text):
        return [float(len(text)), 1.0, 0.0]


@pytest.fixture
def indice_local(monkeypatch, tmp_path):
    monkeypatch.setattr(rag, "CHROMA_DIR", str(tmp_path / "chroma"))
    monkeypatch.setattr(rag, "_emb", lambda: EmbeddingsSimulados())


def test_nuevo_documento_reemplaza_el_anterior(indice_local):
    rag.indexar("Empresa A: activo corriente 100", "a.csv")
    rag.indexar("Empresa B: activo corriente 200", "b.xlsx")
    fuentes = rag.buscar("activo corriente")
    assert "[b.xlsx #0]" in fuentes
    assert "Empresa B" in fuentes
    assert "Empresa A" not in fuentes
    assert "a.csv" not in fuentes


def test_mismo_nombre_reemplaza_el_contenido(indice_local):
    rag.indexar("Dato anterior 100", "estados.csv")
    rag.indexar("Dato nuevo 200", "estados.csv")
    fuentes = rag.buscar("Dato")
    assert "Dato nuevo 200" in fuentes
    assert "Dato anterior" not in fuentes


def test_indice_vacio_conserva_buscar_compatible_con_crew(indice_local):
    assert rag.buscar("notas") == ""


def test_documento_sin_texto_es_rechazado(indice_local):
    with pytest.raises(ValueError, match="no contiene texto"):
        rag.indexar("", "vacio.pdf")


def test_responder_recibe_fuentes_y_ratios_actuales(monkeypatch):
    fuentes = "[ejemplo_estados.csv #0]\nActivo corriente 2024: 560000"
    ratios = "| periodo | liquidez_corriente |\n| 2024 | 0.8 |"
    llamadas = []
    monkeypatch.setattr(rag, "buscar", lambda pregunta, coleccion: fuentes)

    class ModeloSimulado:
        def __init__(self, **kwargs):
            assert kwargs["model"] == rag.LLM_MODEL
            assert kwargs["num_ctx"] == rag.NUM_CTX

        def invoke(self, mensajes):
            llamadas.append(mensajes)
            return SimpleNamespace(content="La liquidez es 0.8 [Ratios calculados].")

    monkeypatch.setattr(rag, "ChatOllama", ModeloSimulado)
    resultado = rag.responder("Interpreta la liquidez", ratios)
    assert resultado.fuentes == fuentes
    assert resultado.respuesta == "La liquidez es 0.8 [Ratios calculados]."
    assert fuentes in llamadas[0][1][1]
    assert ratios in llamadas[0][1][1]
    assert "Interpreta la liquidez" in llamadas[0][1][1]


def test_sin_evidencia_no_invoca_el_modelo(monkeypatch):
    monkeypatch.setattr(rag, "buscar", lambda pregunta, coleccion: "")

    def modelo_prohibido(**kwargs):
        pytest.fail("No debe generar una respuesta sin evidencia")

    monkeypatch.setattr(rag, "ChatOllama", modelo_prohibido)
    resultado = rag.responder("¿Quién es el auditor?")
    assert resultado.respuesta.startswith("No aparece en el documento")
    assert resultado.fuentes == ""


def test_pregunta_vacia_es_rechazada():
    with pytest.raises(ValueError, match="Escribe una pregunta"):
        rag.responder("   ")


def test_error_del_modelo_se_propaga(monkeypatch):
    monkeypatch.setattr(rag, "buscar", lambda pregunta, coleccion: "[a.csv #0]\nDatos")

    class ModeloNoDisponible:
        def __init__(self, **kwargs):
            pass

        def invoke(self, mensajes):
            raise ConnectionError("Ollama no disponible")

    monkeypatch.setattr(rag, "ChatOllama", ModeloNoDisponible)
    with pytest.raises(ConnectionError, match="Ollama no disponible"):
        rag.responder("¿Cuál es el activo?")