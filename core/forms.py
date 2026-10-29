from django import forms


class BootstrapFormMixin:
    """Agrega clases de Bootstrap a los widgets de un formulario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "form-select")
            elif isinstance(widget, (forms.RadioSelect, forms.CheckboxSelectMultiple)):
                continue
            else:
                widget.attrs.setdefault("class", "form-control")

    def add_error(self, field, error):
        super().add_error(field, error)
        if not field or field not in self.fields:
            return
        widget = self.fields[field].widget
        classes = widget.attrs.get("class", "")
        if "is-invalid" not in classes:
            widget.attrs["class"] = f"{classes} is-invalid".strip()
