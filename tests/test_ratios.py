from src.schemas import EstadosFinancieros
from src.ratios import calcular_ratios, tabla_ratios, alertas


def test_ratios_basicos():
    e = EstadosFinancieros(periodo="2024", activo_corriente=200, pasivo_corriente=100,
                           inventarios=50, activo_total=1000, pasivo_total=600,
                           patrimonio=400, ventas=500, costo_ventas=300,
                           utilidad_operativa=80, depreciacion_amortizacion=20,
                           gastos_financieros=40, utilidad_neta=40)
    r = calcular_ratios(e)
    assert r["liquidez_corriente"] == 2.0
    assert r["prueba_acida"] == 1.5
    assert r["endeudamiento"] == 0.6
    assert r["margen_bruto"] == 0.4
    assert r["roe"] == 0.1
    assert r["ebitda"] == 100
    assert r["cobertura_intereses"] == 2.0


def test_division_por_cero_devuelve_none():
    r = calcular_ratios(EstadosFinancieros(periodo="2024", activo_corriente=10, pasivo_corriente=0))
    assert r["liquidez_corriente"] is None


def test_alerta_liquidez():
    df = tabla_ratios([EstadosFinancieros(periodo="2024", activo_corriente=50, pasivo_corriente=100)])
    assert any("liquidez" in a for a in alertas(df))
