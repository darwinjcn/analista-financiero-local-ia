"""Lectura de PDF y Excel/CSV a texto plano y tablas."""
from io import BytesIO
import pandas as pd
import pdfplumber
from .tabular_extractor import es_periodo


def leer_pdf(data: bytes) -> str:
    partes = []
    with pdfplumber.open(BytesIO(data)) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            texto = page.extract_text() or ""
            for tabla in page.extract_tables():
                df = pd.DataFrame(tabla)
                texto += "\n" + df.to_markdown(index=False)
            partes.append(f"--- Página {i} ---\n{texto}")
    return "\n".join(partes)


def _df_a_texto_transpuesto(df: pd.DataFrame) -> str:
    """Si el df tiene formato cuenta×periodo, lo transpone para que cada
    periodo sea una fila (mejor para RAG y para fallback del LLM)."""
    if df.empty or len(df.columns) < 2:
        return df.to_markdown(index=False)
    col_cuenta = df.columns[0]
    col_periodos = [c for c in df.columns[1:] if es_periodo(c)]
    if not col_periodos:
        return df.to_markdown(index=False)
    df_t = df.set_index(col_cuenta).T
    df_t.index.name = "periodo"
    return df_t.to_markdown()


def leer_tabular(data: bytes, nombre: str) -> tuple[str, pd.DataFrame]:
    if nombre.lower().endswith(".csv"):
        df = pd.read_csv(BytesIO(data))
        return _df_a_texto_transpuesto(df), df
    else:
        hojas = pd.read_excel(BytesIO(data), sheet_name=None)
        partes, dfs = [], []
        for nombre_hoja, df in hojas.items():
            partes.append(f"\n{'='*40}\nHOJA: {nombre_hoja}\n{'='*40}\n")
            partes.append(_df_a_texto_transpuesto(df))
            dfs.append(df)
        return "\n".join(partes), (dfs[0] if dfs else pd.DataFrame())


def leer_archivo(data: bytes, nombre: str) -> str:
    if nombre.lower().endswith(".pdf"):
        return leer_pdf(data)
    texto, _ = leer_tabular(data, nombre)
    return texto