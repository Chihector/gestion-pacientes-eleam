from django import template

register = template.Library()

_MODEL_LABELS = {
    "accounts.User": "Usuario",
    "residents.Resident": "Residente",
    "residents.Contact": "Contacto",
    "residents.Disease": "Enfermedad / Diagnóstico",
    "residents.Medication": "Medicamento / Remedio",
    "care.CarePlan": "Plan de cuidados",
    "care.DailyCareRecord": "Registro diario de cuidado",
    "incidents.IncidentReport": "Reporte de incidente",
}


@register.filter
def model_friendly(value: str) -> str:
    return _MODEL_LABELS.get(value, value)
