from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from accounts.models import Role
from audit.models import AuditedModel
from residents.models import Resident


def shift_for_time(value) -> str:
    """Sugiere el turno según la hora local del registro."""
    hour = timezone.localtime(value).hour
    if 7 <= hour < 15:
        return DailyCareRecord.Shift.MANANA
    if 15 <= hour < 23:
        return DailyCareRecord.Shift.TARDE
    return DailyCareRecord.Shift.NOCHE


class CarePlan(AuditedModel):
    """Plan de cuidados acordado por Enfermería para un residente."""

    class Status(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        CERRADO = "CERRADO", "Cerrado"

    resident = models.ForeignKey(
        Resident,
        verbose_name="residente",
        related_name="care_plans",
        on_delete=models.CASCADE,
    )
    title = models.CharField("necesidad o foco", max_length=150)
    need = models.TextField(
        "descripción de la necesidad",
        blank=True,
        help_text="Qué se observó y por qué requiere un plan de cuidado.",
    )
    objective = models.TextField("objetivo")
    actions = models.TextField(
        "acciones acordadas",
        help_text="Actividades concretas que realizará el equipo.",
    )
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="responsable principal",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="care_plans",
        limit_choices_to={"is_active": True},
    )
    start_date = models.DateField("fecha de inicio", default=timezone.localdate)
    review_date = models.DateField("próxima revisión", null=True, blank=True)
    status = models.CharField(
        "estado", max_length=20, choices=Status.choices, default=Status.ACTIVO
    )
    notes = models.TextField("observaciones", blank=True)
    closure_reason = models.TextField(
        "motivo de cierre",
        blank=True,
        help_text="Se completa al cerrar el plan.",
    )

    class Meta:
        verbose_name = "plan de cuidados"
        verbose_name_plural = "planes de cuidados"
        ordering = ["-start_date", "-pk"]
        indexes = [
            models.Index(fields=["resident", "status"]),
            models.Index(fields=["status", "review_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} · {self.resident}"

    def clean(self):
        super().clean()
        errors = {}
        if (
            self.start_date
            and self.review_date
            and self.review_date < self.start_date
        ):
            errors["review_date"] = (
                "La próxima revisión no puede ser anterior al inicio del plan."
            )
        if self.start_date and self.start_date > timezone.localdate():
            errors["start_date"] = "La fecha de inicio no puede ser futura."
        if errors:
            raise ValidationError(errors)

    def get_absolute_url(self) -> str:
        return f"{reverse('residents:detail', kwargs={'pk': self.resident_id})}#cuidados"

    @property
    def is_open(self) -> bool:
        return self.status == self.Status.ACTIVO


class DailyCareRecord(AuditedModel):
    """Registro de un cuidado realizado durante un turno.

    Los registros no se editan ni se eliminan: una corrección crea una nueva
    versión enlazada y deja la anterior marcada como corregida.
    """

    class Shift(models.TextChoices):
        MANANA = "MANANA", "Mañana"
        TARDE = "TARDE", "Tarde"
        NOCHE = "NOCHE", "Noche"

    class Category(models.TextChoices):
        ALIMENTACION = "ALIMENTACION", "Alimentación"
        HIDRATACION = "HIDRATACION", "Hidratación"
        ELIMINACION = "ELIMINACION", "Eliminación"
        MOVILIDAD = "MOVILIDAD", "Movilidad"
        SUENO = "SUENO", "Sueño y descanso"
        HIGIENE = "HIGIENE", "Higiene y confort"
        ACTIVIDAD = "ACTIVIDAD", "Actividad y acompañamiento"
        OTRO = "OTRO", "Otro cuidado"

    class Status(models.TextChoices):
        VIGENTE = "VIGENTE", "Vigente"
        CORREGIDO = "CORREGIDO", "Corregido"

    resident = models.ForeignKey(
        Resident,
        verbose_name="residente",
        related_name="daily_records",
        on_delete=models.CASCADE,
    )
    care_plan = models.ForeignKey(
        CarePlan,
        verbose_name="plan de cuidados",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="records",
    )
    recorded_at = models.DateTimeField("fecha y hora", default=timezone.now)
    shift = models.CharField("turno", max_length=10, choices=Shift.choices)
    category = models.CharField(
        "categoría", max_length=20, choices=Category.choices
    )
    description = models.TextField("descripción del cuidado")
    observations = models.TextField(
        "observaciones para el equipo",
        blank=True,
        help_text="Información útil para el próximo turno o para Enfermería.",
    )
    requires_nursing_review = models.BooleanField(
        "requiere revisión de Enfermería",
        default=False,
        help_text="Márcalo si el registro necesita validación o seguimiento.",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="revisado por",
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    reviewed_at = models.DateTimeField(
        "revisado el", null=True, blank=True, editable=False
    )
    review_notes = models.TextField("observaciones de la revisión", blank=True)
    status = models.CharField(
        "estado", max_length=20, choices=Status.choices, default=Status.VIGENTE
    )
    supersedes = models.OneToOneField(
        "self",
        verbose_name="reemplaza a",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="correction",
        help_text="Registro anterior que esta versión corrige.",
    )
    correction_reason = models.TextField(
        "motivo de la corrección",
        blank=True,
        help_text="Obligatorio cuando esta versión corrige un registro anterior.",
    )

    class Meta:
        verbose_name = "registro diario de cuidado"
        verbose_name_plural = "registros diarios de cuidado"
        ordering = ["-recorded_at", "-pk"]
        indexes = [
            models.Index(fields=["resident", "-recorded_at"]),
            models.Index(fields=["status", "requires_nursing_review"]),
            models.Index(fields=["recorded_at"]),
        ]

    def __str__(self) -> str:
        when = (
            timezone.localtime(self.recorded_at) if self.recorded_at else None
        )
        stamp = f" · {when:%d/%m/%Y %H:%M}" if when else ""
        return f"{self.get_category_display()} · {self.resident}{stamp}"

    def clean(self):
        super().clean()
        errors = {}
        if self.recorded_at:
            value = self.recorded_at
            if timezone.is_naive(value):
                value = timezone.make_aware(value)
            if value > timezone.now() + timedelta(minutes=5):
                errors["recorded_at"] = "La fecha y hora no puede ser futura."
            if self.resident_id and self.resident.admission_date:
                if timezone.localtime(value).date() < self.resident.admission_date:
                    errors["recorded_at"] = (
                        "La fecha no puede ser anterior al ingreso del residente."
                    )
        if self.care_plan_id and self.resident_id:
            if self.care_plan.resident_id != self.resident_id:
                errors["care_plan"] = (
                    "El plan de cuidados pertenece a otro residente."
                )
        if self.supersedes_id and not (self.correction_reason or "").strip():
            errors["correction_reason"] = (
                "Explica brevemente por qué se corrige el registro."
            )
        if errors:
            raise ValidationError(errors)

    def get_absolute_url(self) -> str:
        return reverse("care:record_detail", kwargs={"pk": self.pk})

    @property
    def is_corrected(self) -> bool:
        return self.status == self.Status.CORREGIDO

    @property
    def is_reviewed(self) -> bool:
        return self.reviewed_at is not None

    @property
    def review_pending(self) -> bool:
        return (
            self.status == self.Status.VIGENTE
            and self.requires_nursing_review
            and self.reviewed_at is None
        )

    @property
    def correction_record(self) -> DailyCareRecord | None:
        """Versión que reemplazó a este registro, si existe."""
        return getattr(self, "correction", None)

    def is_owned_or_nurse(self, user) -> bool:
        """Indica si el usuario es autor del registro o parte de Enfermería."""
        if not getattr(user, "is_authenticated", False):
            return False
        return bool(
            user.is_superuser
            or user.role == Role.ENFERMERIA
            or self.created_by_id == user.pk
        )

    def can_be_corrected_by(self, user) -> bool:
        return self.status == self.Status.VIGENTE and self.is_owned_or_nurse(
            user
        )

    def can_be_reviewed_by(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        return self.review_pending and bool(
            user.is_superuser or user.role == Role.ENFERMERIA
        )
