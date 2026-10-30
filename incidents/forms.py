from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.forms import BootstrapFormMixin
from residents.models import Resident

from .models import Incident


class IncidentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            "resident",
            "occurred_at",
            "incident_type",
            "location",
            "severity",
            "description",
            "actions_taken",
            "witnesses",
            "notified_to",
            "notify_family",
            "notify_direction",
        ]
        widgets = {
            "occurred_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describe los hechos observados, en orden, sin opiniones ni diagnósticos.",
                }
            ),
            "actions_taken": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Describe las acciones inmediatas que se tomaron y a quién se avisó.",
                }
            ),
            "witnesses": forms.TextInput(
                attrs={"placeholder": "Solo si es necesario para el seguimiento"}
            ),
        }
        help_texts = {
            "severity": "Apreciación inicial; no reemplaza la evaluación de Enfermería.",
            "description": "Registra hechos. Este reporte no reemplaza el aviso inmediato ni los protocolos del ELEAM.",
            "witnesses": "Evita incluir datos personales que no sean necesarios.",
        }
        labels = {
            "notify_family": "Se debe notificar a familia o representante",
            "notify_direction": "Se debe notificar a Dirección",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resident"].queryset = Resident.objects.filter(
            is_active=True
        ).order_by("last_name", "first_name")
        self.fields["resident"].label_from_instance = (
            lambda resident: f"{resident.full_name} · Hab. {resident.room or '—'}"
        )
        if not self.is_bound:
            self.initial.setdefault(
                "occurred_at",
                timezone.localtime().replace(second=0, microsecond=0),
            )

    def clean_occurred_at(self):
        value = self.cleaned_data.get("occurred_at")
        if not value:
            return value
        if timezone.is_naive(value):
            value = timezone.make_aware(value)
        if value > timezone.now() + timedelta(minutes=5):
            raise ValidationError("La fecha y hora del incidente no puede ser futura.")
        resident = self.cleaned_data.get("resident")
        if resident and resident.admission_date:
            if timezone.localtime(value).date() < resident.admission_date:
                raise ValidationError(
                    "La fecha no puede ser anterior al ingreso del residente."
                )
        return value

    def clean_description(self):
        value = (self.cleaned_data.get("description") or "").strip()
        if len(value) < 10:
            raise ValidationError(
                "Describe lo ocurrido con al menos 10 caracteres."
            )
        return value

    def clean_actions_taken(self):
        value = (self.cleaned_data.get("actions_taken") or "").strip()
        if len(value) < 10:
            raise ValidationError(
                "Describe las acciones tomadas con al menos 10 caracteres."
            )
        return value


class IncidentCloseForm(BootstrapFormMixin, forms.Form):
    close_reason = forms.CharField(
        label="Seguimiento y motivo de cierre",
        min_length=10,
        max_length=1000,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Indica qué seguimiento se realizó; no sustituye los protocolos institucionales.",
    )


class IncidentFilterForm(BootstrapFormMixin, forms.Form):
    desde = forms.DateField(
        label="Desde",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    hasta = forms.DateField(
        label="Hasta",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    tipo = forms.ChoiceField(
        label="Tipo",
        required=False,
        choices=[("", "Todos"), *Incident.Type.choices],
    )
    estado = forms.ChoiceField(
        label="Estado",
        required=False,
        choices=[("", "Todos"), *Incident.Status.choices],
    )

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("desde")
        end = cleaned.get("hasta")
        if start and end and end < start:
            self.add_error("hasta", "La fecha final no puede ser anterior a la inicial.")
        return cleaned


class IncidentReportForm(BootstrapFormMixin, forms.Form):
    desde = forms.DateField(
        label="Desde",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    hasta = forms.DateField(
        label="Hasta",
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("desde")
        end = cleaned.get("hasta")
        if start and end and end < start:
            self.add_error("hasta", "La fecha final no puede ser anterior a la inicial.")
        return cleaned
