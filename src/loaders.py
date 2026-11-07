"""Lectura de PDF y Excel/CSV a texto plano y tablas."""
from io import BytesIO
import pandas as pd
import pdfplumber


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


def leer_tabular(data: bytes, nombre: str) -> tuple[str, pd.DataFrame]:
    if nombre.lower().endswith(".csv"):
        df = pd.read_csv(BytesIO(data))
    else:
        df = pd.read_excel(BytesIO(data))
    return df.to_markdown(index=False), df


def leer_archivo(data: bytes, nombre: str) -> str:
    if nombre.lower().endswith(".pdf"):
        return leer_pdf(data)
    texto, _ = leer_tabular(data, nombre)
    return texto
