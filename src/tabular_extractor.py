"""Extracción determinista (sin LLM) de cifras desde CSV/Excel con formato cuenta × periodo."""
import re
import unicodedata
from io import BytesIO
import pandas as pd
from .schemas import EstadosFinancieros

MAPA_CUENTAS = {
    # Español
    "efectivo": "efectivo",
    "caja": "efectivo",
    "inventarios": "inventarios",
    "inventario": "inventarios",
    "activo corriente": "activo_corriente",
    "activo total": "activo_total",
    "pasivo corriente": "pasivo_corriente",
    "pasivo total": "pasivo_total",
    "patrimonio": "patrimonio",
    "ventas": "ventas",
    "costo de ventas": "costo_ventas",
    "utilidad operativa": "utilidad_operativa",
    "depreciacion y amortizacion": "depreciacion_amortizacion",
    "depreciacion o amortizacion": "depreciacion_amortizacion",
    "gastos financieros": "gastos_financieros",
    "utilidad neta": "utilidad_neta",
    
    # English
    "cash": "efectivo",
    "cash and equivalents": "efectivo",
    "inventories": "inventarios",
    "inventory": "inventarios",
    "current assets": "activo_corriente",
    "total assets": "activo_total",
    "current liabilities": "pasivo_corriente",
    "total liabilities": "pasivo_total",
    "equity": "patrimonio",
    "shareholders equity": "patrimonio",
    "stockholders equity": "patrimonio",
    "revenue": "ventas",
    "sales": "ventas",
    "net sales": "ventas",
    "cost of sales": "costo_ventas",
    "cost of goods sold": "costo_ventas",
    "cogs": "costo_ventas",
    "operating income": "utilidad_operativa",
    "operating profit": "utilidad_operativa",
    "ebit": "utilidad_operativa",
    "depreciation and amortization": "depreciacion_amortizacion",
    "depreciation": "depreciacion_amortizacion",
    "amortization": "depreciacion_amortizacion",
    "financial expenses": "gastos_financieros",
    "interest expense": "gastos_financieros",
    "interest expenses": "gastos_financieros",
    "net income": "utilidad_neta",
    "net profit": "utilidad_neta",
    "profit": "utilidad_neta",
}

def _normalizar(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9\s]", "", s.lower())
    return re.sub(r"\s+", " ", s).strip()

def es_periodo(col) -> bool:
    """Detecta si una cabecera parece un periodo (año o rango tipo 2023-2024)."""
    s = str(col).strip()
    return bool(re.fullmatch(r"(19|20)\d{2}", s)) or \
           bool(re.fullmatch(r"(19|20)\d{2}\s*[-/]\s*(19|20)\d{2}", s))

def _extraer_de_df(df: pd.DataFrame) -> list[EstadosFinancieros]:
    if df.empty or len(df.columns) < 2:
        return []
    col_cuenta = df.columns[0]
    col_periodos = [c for c in df.columns[1:] if es_periodo(c)]
    if not col_periodos:
        return []

    # Mapear filas de cuentas a campos del schema
    mapeo = {}
    for _, fila in df.iterrows():
        nombre = _normalizar(fila[col_cuenta])
        if nombre in MAPA_CUENTAS:
            mapeo[MAPA_CUENTAS[nombre]] = fila

    if not mapeo:
        return []

    # Un objeto EstadosFinancieros por cada columna de periodo
    estados = []
    for periodo in col_periodos:
        row = {"periodo": str(periodo)}
        for campo, fila in mapeo.items():
            val = fila[periodo]
            if pd.isna(val):
                row[campo] = None
            else:
                try:
                    row[campo] = float(val)
                except (ValueError, TypeError):
                    row[campo] = None
        estados.append(EstadosFinancieros(**row))
    return estados

def extraer_tabular(data: bytes, nombre: str) -> list[EstadosFinancieros]:
    """Intenta extracción determinista. Devuelve [] si el formato no es reconocible."""
    try:
        if nombre.lower().endswith(".csv"):
            df = pd.read_csv(BytesIO(data))
            return _extraer_de_df(df)
        else:
            hojas = pd.read_excel(BytesIO(data), sheet_name=None)
            for df in hojas.values():
                resultado = _extraer_de_df(df)
                if resultado:
                    return resultado
            return []
    except Exception:
        return []