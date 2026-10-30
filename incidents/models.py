from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from audit.models import AuditedModel
from residents.models import Resident


class Incident(AuditedModel):
    class Type(models.TextChoices):
        FALL = "CAIDA", "Caída"
        INJURY = "LESION", "Lesión sin caída"
        MEDICATION_ERROR = "ERROR_MEDICACION", "Error de medicación"
        DISORIENTATION = "DESORIENTACION", "Confusión o desorientación"
        UNAUTHORIZED_EXIT = "SALIDA_NO_AUTORIZADA", "Salida no autorizada"
        AGGRESSION = "AGRESION", "Agresión"
        OTHER = "OTRO", "Otro"

    class Severity(models.TextChoices):
        MINOR = "LEVE", "Leve"
        MODERATE = "MODERADO", "Moderado"
        SERIOUS = "GRAVE", "Grave"

    class Status(models.TextChoices):
        OPEN = "ABIERTO", "Abierto"
        CLOSED = "CERRADO", "Cerrado"

    resident = models.ForeignKey(
        Resident,
        verbose_name="residente",
        related_name="incidents",
        on_delete=models.PROTECT,
    )
    occurred_at = models.DateTimeField("fecha y hora del incidente")
    incident_type = models.CharField(
        "tipo de incidente", max_length=30, choices=Type.choices
    )
    location = models.CharField("lugar", max_length=150, blank=True)
    severity = models.CharField(
        "gravedad percibida", max_length=10, choices=Severity.choices
    )
    description = models.TextField("qué ocurrió")
    actions_taken = models.TextField("acciones inmediatas tomadas")
    witnesses = models.CharField("personas presentes", max_length=500, blank=True)
    notified_to = models.CharField("a quién se avisó", max_length=150, blank=True)
    notify_family = models.BooleanField(
        "se debe notificar a familia o representante", default=False
    )
    notify_direction = models.BooleanField(
        "se debe notificar a Dirección", default=False
    )
    status = models.CharField(
        "estado", max_length=10, choices=Status.choices, default=Status.OPEN
    )
    close_reason = models.TextField("seguimiento y motivo de cierre", blank=True)
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="cerrado por",
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    closed_at = models.DateTimeField("cerrado el", null=True, blank=True, editable=False)

    class Meta:
        verbose_name = "incidente"
        verbose_name_plural = "incidentes"
        ordering = ["-occurred_at", "-pk"]
        indexes = [
            models.Index(fields=["occurred_at"]),
            models.Index(fields=["status", "occurred_at"]),
            models.Index(fields=["incident_type", "occurred_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_incident_type_display()} · {self.resident}"

    def clean(self):
        super().clean()
        errors = {}
        if self.occurred_at:
            occurred_at = self.occurred_at
            if timezone.is_naive(occurred_at):
                occurred_at = timezone.make_aware(occurred_at)
            if occurred_at > timezone.now() + timedelta(minutes=5):
                errors["occurred_at"] = (
                    "La fecha y hora del incidente no puede ser futura."
                )
            if self.resident_id and self.resident.admission_date:
                if timezone.localtime(occurred_at).date() < self.resident.admission_date:
                    errors["occurred_at"] = (
                        "La fecha no puede ser anterior al ingreso del residente."
                    )
        if errors:
            raise ValidationError(errors)

    def get_absolute_url(self) -> str:
        return reverse("incidents:detail", kwargs={"pk": self.pk})

    @property
    def is_open(self) -> bool:
        return self.status == self.Status.OPEN
