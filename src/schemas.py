"""Estructura de datos que el LLM debe devolver (salida JSON validada)."""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class EstadosFinancieros(BaseModel):
    periodo: str = Field(description="Año o periodo, ej. 2024")

    @field_validator("periodo", mode="before")
    @classmethod
    def normalizar_periodo(cls, value):
        """Ollama puede devolver los años como números en el JSON."""
        if isinstance(value, int) and not isinstance(value, bool):
            return str(value)
        return value

    moneda: Optional[str] = None
    # Balance general
    activo_corriente: Optional[float] = None
    activo_total: Optional[float] = None
    inventarios: Optional[float] = None
    efectivo: Optional[float] = None
    pasivo_corriente: Optional[float] = None
    pasivo_total: Optional[float] = None
    patrimonio: Optional[float] = None
    # Estado de resultados
    ventas: Optional[float] = None
    costo_ventas: Optional[float] = None
    utilidad_operativa: Optional[float] = None
    depreciacion_amortizacion: Optional[float] = None
    gastos_financieros: Optional[float] = None
    utilidad_neta: Optional[float] = None
