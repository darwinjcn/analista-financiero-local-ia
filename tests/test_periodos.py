import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from src import extractor
from src.loaders import leer_archivo
from src.schemas import EstadosFinancieros


def test_periodo_numerico_se_convierte_a_texto():
    assert EstadosFinancieros(periodo=2023).periodo == "2023"


def test_periodo_textual_se_conserva():
    assert EstadosFinancieros(periodo="2024-T1").periodo == "2024-T1"


@pytest.mark.parametrize("periodo", [None, True, [], {}, 2023.5])
def test_periodos_invalidos_siguen_rechazandose(periodo):
    with pytest.raises(ValidationError):
        EstadosFinancieros(periodo=periodo)


@pytest.mark.parametrize("extension", ["csv", "xlsx", "pdf"])
def test_lectura_y_extraccion_con_anios_numericos(monkeypatch, extension):
    path = Path(__file__).resolve().parents[1] / "data" / f"ejemplo_estados.{extension}"
    texto = leer_archivo(path.read_bytes(), path.name)
    assert "2023" in texto and "2024" in texto
    prompts = []

    class OllamaSimulado:
        def __init__(self, **kwargs):
            pass

        def invoke(self, prompt):
            prompts.append(prompt)
            return SimpleNamespace(content=json.dumps({"periodos": [
                {"periodo": 2023, "activo_corriente": 520000},
                {"periodo": 2024, "activo_corriente": 560000},
            ]}))

    monkeypatch.setattr(extractor, "ChatOllama", OllamaSimulado)
    estados = extractor.extraer_estados(texto)
    assert [e.periodo for e in estados] == ["2023", "2024"]
    assert [e.activo_corriente for e in estados] == [520000, 560000]
    assert texto in prompts[0]