from django import template

register = template.Library()

_MODEL_LABELS = {
    "accounts.User": "Usuario",
    "residents.Resident": "Residente",
    "residents.Contact": "Contacto",
}


@register.filter
def model_friendly(value: str) -> str:
    return _MODEL_LABELS.get(value, value)
