import sys
from io import BytesIO
from pathlib import Path
from types import ModuleType, SimpleNamespace

import streamlit as st
from streamlit.testing.v1 import AppTest

from src import extractor, rag
from src.schemas import EstadosFinancieros


def test_consulta_muestra_respuesta_fuentes_y_descarta_archivo_anterior(monkeypatch):
    archivo = BytesIO(b"periodo,activo_corriente,pasivo_corriente\n2024,200,100\n")
    archivo.name = "actual.csv"
    activo = [archivo]
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: activo[0])
    monkeypatch.setattr(rag, "indexar", lambda *args: None)
    monkeypatch.setattr(extractor, "extraer_estados", lambda texto: [
        EstadosFinancieros(periodo="2024", activo_corriente=200, pasivo_corriente=100)
    ])
    consultas = []

    def responder(pregunta, ratios):
        consultas.append((pregunta, ratios))
        return rag.RespuestaRAG("La liquidez es 2.0 [Ratios calculados].",
                                "[actual.csv #0]\n2024: activo corriente 200")

    monkeypatch.setattr(rag, "responder", responder)
    crew_simulado = ModuleType("src.crew")
    crew_simulado.generar_informe = lambda *args: "Informe simulado"
    monkeypatch.setitem(sys.modules, "src.crew", crew_simulado)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
    app.run()
    app.button[0].click().run()
    assert not app.exception
    app.text_input(key="pregunta_rag").set_value("Interpreta la liquidez")
    next(b for b in app.button if b.label == "Responder pregunta").click().run()
    assert not app.exception
    assert consultas[0][0] == "Interpreta la liquidez"
    assert "liquidez_corriente" in consultas[0][1]
    assert any("La liquidez es 2.0" in m.value for m in app.markdown)
    assert any("[actual.csv #0]" in t.value for t in app.text)
    app.run()
    assert len(consultas) == 1  # No vuelve a llamar al modelo en cada cambio de pantalla.
    activo[0] = None
    app.run()
    assert "estados" not in app.session_state
    assert "respuesta_rag" not in app.session_state
    assert not app.exception