from django.db import models


class TimeStampedModel(models.Model):
    """Fechas de creación y actualización para todos los modelos auditables."""

    created_at = models.DateTimeField("creado el", auto_now_add=True, editable=False)
    updated_at = models.DateTimeField("actualizado el", auto_now=True, editable=False)

    class Meta:
        abstract = True
