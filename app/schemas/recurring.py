from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
import re

class RecurringCreateRequest(BaseModel):
    Title: str
    Description: Optional[str] = None
    Priority: Optional[int] = None
    Frequency: Optional[str] = None
    DayNameFrequency: Optional[str] = None
    DayFrequency: Optional[str] = None

    @model_validator(mode="after")
    def validate_exclusive_fields(self):
        """Asegura que solo uno de los campos Frequency, DayNameFrequency o DayFrequency esté lleno."""
        filled_fields = sum(bool(field) for field in [self.Frequency, self.DayNameFrequency, self.DayFrequency])

        if filled_fields > 1:
            raise ValueError("Solo uno de los campos Frequency, DayNameFrequency o DayFrequency puede estar completo.")
        if filled_fields == 0:
            raise ValueError("Debe completarse uno de los campos: Frequency, DayNameFrequency o DayFrequency.")

        return self

    @field_validator('Frequency')
    def validate_frequency(cls, value):
        """Valida que Frequency sea 'diaria', 'semanal' o 'mensual'."""
        allowed = ["diaria", "semanal", "mensual"]
        if value and value.lower() not in allowed:
            raise ValueError(f"Frequency debe ser uno de: {', '.join(allowed)}.")
        return value

    @field_validator('DayNameFrequency')
    def validate_daynamefrequency(cls, value):
        """Valida que DayNameFrequency solo contenga días válidos: Lu, Ma, Mi, Ju, Vi, Sa, Do."""
        if value:
            valid_days = {"Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"}
            days = {day.strip() for day in value.split(",")}
            invalid_days = days - valid_days
            if invalid_days:
                raise ValueError(f"DayNameFrequency contiene días inválidos: {', '.join(invalid_days)}. "
                                 f"Usa combinaciones de: {', '.join(valid_days)}.")
        return value

    @field_validator('DayFrequency')
    def validate_dayfrequency(cls, value):
        """Valida que DayFrequency sea una combinación de números del 1 al 31 separados por comas."""
        if value:
            if not re.match(r'^(\d{1,2})(,\d{1,2})*$', value.strip()):
                raise ValueError("DayFrequency debe ser una combinación de números separados por comas. Ej: '1,15,30'.")
            days = [int(day.strip()) for day in value.split(",")]
            invalid_days = [str(day) for day in days if not (1 <= day <= 31)]
            if invalid_days:
                raise ValueError(f"DayFrequency contiene valores inválidos: {', '.join(invalid_days)}. Deben estar entre 1 y 31.")
        return value
    
class RecurringUpdateRequest(BaseModel):
    Title: Optional[str] = None
    Description: Optional[str] = None
    Priority: Optional[int] = None