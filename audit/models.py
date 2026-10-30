from __future__ import annotations

import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from core.models import TimeStampedModel


class AuditedModel(TimeStampedModel):
    """Modelo con autoría automática y registro en la auditoría."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="creado por",
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="actualizado por",
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        abstract = True


class AuditLog(models.Model):
    """Registro append-only de cambios relevantes."""

    class Action(models.TextChoices):
        CREATE = "CREATE", "Creado"
        UPDATE = "UPDATE", "Modificado"
        ARCHIVE = "ARCHIVE", "Archivado"
        RESTORE = "RESTORE", "Reactivado"
        DELETE = "DELETE", "Eliminado"
        PASSWORD = "PASSWORD", "Contraseña cambiada"
        PASSWORD_RESET = "PASSWORD_RESET", "Contraseña restablecida"
        DEACTIVATE = "DEACTIVATE", "Usuario desactivado"
        REACTIVATE = "REACTIVATE", "Usuario reactivado"
        CORRECTION = "CORRECTION", "Corregido"
        REVIEW = "REVIEW", "Revisado"
        CLOSE = "CLOSE", "Cerrado"
        EXPORT = "EXPORT", "Exportado"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="actor",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_entries",
    )
    actor_repr = models.CharField("actor (texto)", max_length=254, blank=True)
    action = models.CharField("acción", max_length=20, choices=Action.choices)
    model_label = models.CharField("modelo", max_length=100)
    object_id = models.CharField("id del objeto", max_length=64)
    object_repr = models.CharField("registro afectado", max_length=200)
    changes = models.JSONField(
        "cambios", default=dict, blank=True, encoder=DjangoJSONEncoder
    )
    ip_address = models.GenericIPAddressField("dirección IP", null=True, blank=True)
    created_at = models.DateTimeField("fecha", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "registro de auditoría"
        verbose_name_plural = "registros de auditoría"
        ordering = ["-created_at", "-pk"]
        indexes = [
            models.Index(fields=["model_label", "object_id"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_action_display()} · {self.object_repr} · {self.created_at:%d/%m/%Y %H:%M}"

    @property
    def actor_display(self) -> str:
        return self.actor_repr or (str(self.actor) if self.actor else "Sistema")

    @property
    def action_css(self) -> str:
        return {
            self.Action.CREATE: "success",
            self.Action.UPDATE: "info",
            self.Action.ARCHIVE: "warning",
            self.Action.RESTORE: "success",
            self.Action.DELETE: "danger",
            self.Action.PASSWORD: "muted",
            self.Action.PASSWORD_RESET: "muted",
            self.Action.DEACTIVATE: "danger",
            self.Action.REACTIVATE: "success",
            self.Action.CORRECTION: "warning",
            self.Action.REVIEW: "info",
            self.Action.CLOSE: "success",
            self.Action.EXPORT: "info",
        }.get(self.action, "muted")

    @property
    def change_list(self) -> list[dict[str, str]]:
        rows = []
        for field_name, data in (self.changes or {}).items():
            if isinstance(data, dict) and "after" in data:
                label = str(data.get("label") or field_name)
                before = data.get("before")
                after = data.get("after")
            else:
                label = field_name
                before = None
                after = data
            rows.append(
                {
                    "field": label,
                    "before": self._format_value(before),
                    "after": self._format_value(after),
                }
            )
        return rows

    @staticmethod
    def _format_value(value) -> str:
        if value is None or value == "":
            return "—"
        if isinstance(value, bool):
            return "Sí" if value else "No"
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)
