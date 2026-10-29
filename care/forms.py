from __future__ import annotations

from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import Role, User
from core.forms import BootstrapFormMixin
from residents.models import Resident

from .models import CarePlan, DailyCareRecord, shift_for_time

CARE_ROLES = (Role.ENFERMERIA, Role.TECNICO, Role.CUIDADOR)


class CarePlanForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CarePlan
        fields = [
            "title",
            "need",
            "objective",
            "actions",
            "responsible",
            "start_date",
            "review_date",
            "notes",
        ]
        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "review_date": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "need": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Ej.: Se levanta de noche sin apoyo y ha tenido dos tropiezos.",
                }
            ),
            "objective": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Ej.: Mantener desplazamientos seguros durante el turno nocturno.",
                }
            ),
            "actions": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Ej.: Acompañar al baño, dejar timbre al alcance y registrar cada salida de la cama.",
                }
            ),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
        help_texts = {
            "title": "Describe el foco en pocas palabras, sin diagnósticos médicos.",
            "need": "Hechos observados por el equipo, no opiniones.",
            "objective": "Resultado esperado y verificable.",
            "actions": "Qué hará el equipo y con qué frecuencia.",
            "review_date": "Fecha acordada para revisar si el plan sigue vigente.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsible"].queryset = User.objects.filter(
            is_active=True, role__in=CARE_ROLES
        ).order_by("last_name", "first_name")
        self.fields["responsible"].label_from_instance = (
            lambda user: user.get_full_name() or user.email
        )

    def clean_start_date(self):
        value = self.cleaned_data.get("start_date")
        if value and value > timezone.localdate():
            raise ValidationError("La fecha de inicio no puede ser futura.")
        return value

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        review = cleaned.get("review_date")
        if start and review and review < start:
            self.add_error(
                "review_date",
                "La próxima revisión no puede ser anterior al inicio del plan.",
            )
        return cleaned


class DailyCareRecordForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = DailyCareRecord
        fields = [
            "resident",
            "care_plan",
            "recorded_at",
            "shift",
            "category",
            "description",
            "observations",
            "requires_nursing_review",
        ]
        widgets = {
            "recorded_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describe lo realizado y lo observado, sin diagnósticos ni opiniones.",
                }
            ),
            "observations": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Ej.: Quedó somnolienta; avisar a Enfermería si continúa en el próximo control.",
                }
            ),
        }
        labels = {
            "requires_nursing_review": "Marcar para que Enfermería revise este registro",
            "care_plan": "Plan de cuidados relacionado (opcional)",
        }
        help_texts = {
            "recorded_at": "Usa la hora real en que ocurrió el cuidado.",
            "description": "Hechos concretos: qué se hizo, cuánto, cómo respondió la persona.",
            "observations": "Solo lo necesario para el próximo turno o para Enfermería.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resident"].queryset = Resident.objects.filter(
            is_active=True
        ).order_by("last_name", "first_name")
        self.fields["resident"].label_from_instance = (
            lambda resident: f"{resident.full_name} · Hab. {resident.room or '—'}"
        )
        self.fields["care_plan"].queryset = CarePlan.objects.filter(
            status=CarePlan.Status.ACTIVO, resident__is_active=True
        ).select_related("resident")
        self.fields["care_plan"].label_from_instance = (
            lambda plan: f"{plan.title} · {plan.resident}"
        )
        if not self.is_bound:
            now = timezone.localtime()
            initial = self.initial
            initial.setdefault("recorded_at", now.replace(second=0, microsecond=0))
            initial.setdefault("shift", shift_for_time(now))

    def _validate_recorded_at(self, value, resident):
        if not value:
            return value
        if timezone.is_naive(value):
            value = timezone.make_aware(value)
        if value > timezone.now() + timedelta(minutes=5):
            raise ValidationError("La fecha y hora no puede ser futura.")
        if resident and resident.admission_date:
            if timezone.localtime(value).date() < resident.admission_date:
                raise ValidationError(
                    "La fecha no puede ser anterior al ingreso del residente."
                )
        return value

    def clean_recorded_at(self):
        value = self.cleaned_data.get("recorded_at")
        return self._validate_recorded_at(value, self.cleaned_data.get("resident"))

    def clean_description(self):
        value = (self.cleaned_data.get("description") or "").strip()
        if len(value) < 10:
            raise ValidationError(
                "Describe el cuidado con al menos 10 caracteres."
            )
        return value

    def clean_observations(self):
        value = (self.cleaned_data.get("observations") or "").strip()
        if len(value) > 1000:
            raise ValidationError(
                "Las observaciones no pueden superar los 1000 caracteres."
            )
        return value

    def clean(self):
        cleaned = super().clean()
        resident = cleaned.get("resident")
        plan = cleaned.get("care_plan")
        if plan and resident and plan.resident_id != resident.pk:
            self.add_error(
                "care_plan", "El plan de cuidados pertenece a otro residente."
            )
        return cleaned


class DailyCareCorrectionForm(BootstrapFormMixin, forms.ModelForm):
    correction_reason = forms.CharField(
        label="Motivo de la corrección",
        required=True,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Ej.: Se registró por error la cantidad de líquido; se corrige según lo observado.",
            }
        ),
        help_text="El registro original se conserva y queda visible en el historial.",
    )

    class Meta:
        model = DailyCareRecord
        fields = [
            "recorded_at",
            "shift",
            "category",
            "description",
            "observations",
            "requires_nursing_review",
            "correction_reason",
        ]
        widgets = {
            "recorded_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "description": forms.Textarea(attrs={"rows": 4}),
            "observations": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "requires_nursing_review": "Marcar para que Enfermería revise la corrección",
        }

    def __init__(self, *args, original=None, **kwargs):
        self.original = original
        super().__init__(*args, **kwargs)

    def _validate_recorded_at(self, value):
        if not value:
            return value
        if timezone.is_naive(value):
            value = timezone.make_aware(value)
        if value > timezone.now() + timedelta(minutes=5):
            raise ValidationError("La fecha y hora no puede ser futura.")
        resident = self.original.resident if self.original else None
        if resident and resident.admission_date:
            if timezone.localtime(value).date() < resident.admission_date:
                raise ValidationError(
                    "La fecha no puede ser anterior al ingreso del residente."
                )
        return value

    def clean_recorded_at(self):
        return self._validate_recorded_at(self.cleaned_data.get("recorded_at"))

    def clean_description(self):
        value = (self.cleaned_data.get("description") or "").strip()
        if len(value) < 10:
            raise ValidationError(
                "Describe el cuidado con al menos 10 caracteres."
            )
        return value

    def clean_observations(self):
        value = (self.cleaned_data.get("observations") or "").strip()
        if len(value) > 1000:
            raise ValidationError(
                "Las observaciones no pueden superar los 1000 caracteres."
            )
        return value

    def clean_correction_reason(self):
        value = (self.cleaned_data.get("correction_reason") or "").strip()
        if len(value) < 10:
            raise ValidationError(
                "Explica el motivo de la corrección con al menos 10 caracteres."
            )
        if len(value) > 500:
            raise ValidationError(
                "El motivo de la corrección no puede superar los 500 caracteres."
            )
        return value
