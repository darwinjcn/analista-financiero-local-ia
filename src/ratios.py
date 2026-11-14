"""Cálculos financieros 100% en Python (deterministas y testeables)."""
from typing import Optional
import pandas as pd
from .schemas import EstadosFinancieros

def _div(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b in (None, 0):
        return None
    return round(a / b, 4)

def calcular_ratios(e: EstadosFinancieros) -> dict:
    ebitda = None
    if e.utilidad_operativa is not None:
        ebitda = e.utilidad_operativa + (e.depreciacion_amortizacion or 0)
    margen_bruto = None
    if e.ventas and e.costo_ventas is not None:
        margen_bruto = round((e.ventas - e.costo_ventas) / e.ventas, 4)
    prueba_acida = None
    if e.activo_corriente is not None:
        prueba_acida = _div(e.activo_corriente - (e.inventarios or 0), e.pasivo_corriente)
    return {
        "periodo": e.periodo,
        "liquidez_corriente": _div(e.activo_corriente, e.pasivo_corriente),
        "prueba_acida": prueba_acida,
        "endeudamiento": _div(e.pasivo_total, e.activo_total),
        "apalancamiento": _div(e.pasivo_total, e.patrimonio),
        "margen_bruto": margen_bruto,
        "margen_neto": _div(e.utilidad_neta, e.ventas),
        "roe": _div(e.utilidad_neta, e.patrimonio),
        "roa": _div(e.utilidad_neta, e.activo_total),
        "ebitda": ebitda,
        "cobertura_intereses": _div(e.utilidad_operativa, e.gastos_financieros),
    }

def tabla_ratios(estados: list[EstadosFinancieros]) -> pd.DataFrame:
    df = pd.DataFrame([calcular_ratios(e) for e in estados])
    return df.sort_values("periodo").reset_index(drop=True)

def agregar_contexto_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega columnas de rango esperado y estado a los ratios principales."""
    df_out = df.copy()
    
    reglas = {
        "liquidez_corriente": {
            "rango": "1.5 - 2.0",
            "eval": lambda x: "✅ Óptimo" if x is not None and 1.5 <= x <= 2.0 else ("⚠️ Bajo" if x is not None and x < 1.5 else ("🔺 Alto" if x is not None else "➖ N/A"))
        },
        "prueba_acida": {
            "rango": "> 1.0",
            "eval": lambda x: "✅ Óptimo" if x is not None and x >= 1.0 else ("⚠️ Bajo" if x is not None else "➖ N/A")
        },
        "endeudamiento": {
            "rango": "< 60%",
            "eval": lambda x: "✅ Saludable" if x is not None and x <= 0.60 else ("⚠️ Alto" if x is not None and x > 0.70 else ("🔶 Moderado" if x is not None else "➖ N/A"))
        },
        "margen_neto": {
            "rango": "> 10%",
            "eval": lambda x: "✅ Positivo" if x is not None and x >= 0.10 else ("⚠️ Bajo" if x is not None and x >= 0 else ("❌ Negativo" if x is not None else "➖ N/A"))
        },
        "roe": {
            "rango": "> 15%",
            "eval": lambda x: "✅ Bueno" if x is not None and x >= 0.15 else ("🔶 Regular" if x is not None and x >= 0.05 else ("❌ Bajo" if x is not None else "➖ N/A"))
        },
    }
    
    for ratio, config in reglas.items():
        if ratio in df_out.columns:
            df_out[f"{ratio}_rango"] = config["rango"]
            df_out[f"{ratio}_estado"] = df_out[ratio].apply(config["eval"])
            
    return df_out

def alertas(df: pd.DataFrame) -> list[str]:
    """Reglas de negocio simples y explicables."""
    out = []
    for _, r in df.iterrows():
        p = r["periodo"]
        if r["liquidez_corriente"] is not None and r["liquidez_corriente"] < 1:
            out.append(f"{p}: liquidez corriente < 1 ({r['liquidez_corriente']}). Riesgo de pago a corto plazo.")
        if r["endeudamiento"] is not None and r["endeudamiento"] > 0.7:
            out.append(f"{p}: endeudamiento > 70% ({r['endeudamiento']:.0%}).")
        if r["cobertura_intereses"] is not None and r["cobertura_intereses"] < 1.5:
            out.append(f"{p}: cobertura de intereses baja ({r['cobertura_intereses']}).")
        if r["margen_neto"] is not None and r["margen_neto"] < 0:
            out.append(f"{p}: pérdida neta (margen {r['margen_neto']:.1%}).")
    return out