from __future__ import annotations

import re
from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from core.forms import BootstrapFormMixin

from .models import Contact, Resident
from .rut import clean_rut, validate_rut


class ResidentAdminForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Resident
        fields = [
            "first_name",
            "last_name",
            "preferred_name",
            "rut",
            "birth_date",
            "sex",
            "room",
            "admission_date",
            "status",
            "health_insurance",
        ]
        widgets = {
            "birth_date": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "admission_date": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "rut": forms.TextInput(
                attrs={"placeholder": "Ej.: 12.345.678-9", "autocomplete": "off"}
            ),
        }

    def clean_rut(self):
        value = clean_rut(self.cleaned_data.get("rut"))
        if not value:
            raise ValidationError("El RUT es obligatorio.")
        if not validate_rut(value):
            raise ValidationError("Ingresa un RUT válido con dígito verificador.")
        queryset = Resident.objects.filter(rut=value)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("Ya existe una ficha con este RUT.")
        return value

    def clean_birth_date(self):
        value = self.cleaned_data.get("birth_date")
        if value and value > date.today():
            raise ValidationError("La fecha de nacimiento no puede ser futura.")
        return value

    def clean_admission_date(self):
        value = self.cleaned_data.get("admission_date")
        if value and value > date.today():
            raise ValidationError("La fecha de ingreso no puede ser futura.")
        return value

    def clean(self):
        cleaned = super().clean()
        birth_date = cleaned.get("birth_date")
        admission_date = cleaned.get("admission_date")
        if birth_date and admission_date and admission_date < birth_date:
            self.add_error(
                "admission_date",
                "La fecha de ingreso no puede ser anterior al nacimiento.",
            )
        return cleaned


class ResidentClinicalForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Resident
        fields = ["allergies", "relevant_background", "clinical_notes"]
        labels = {
            "allergies": "Alergias conocidas",
            "relevant_background": "Antecedentes relevantes",
            "clinical_notes": "Observaciones para el cuidado",
        }
        widgets = {
            "allergies": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Ej.: Penicilina, látex, sulfas"}
            ),
            "relevant_background": forms.Textarea(attrs={"rows": 4}),
            "clinical_notes": forms.Textarea(attrs={"rows": 4}),
        }
        help_texts = {
            "allergies": "Si no hay alergias registradas, deja el campo vacío; no escribas 'ninguna' sin confirmarlo.",
            "relevant_background": "Registra solo información necesaria para el cuidado. No agregues diagnósticos innecesarios.",
            "clinical_notes": "Observaciones acotadas y útiles para el equipo.",
        }


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "relationship", "phone", "email", "is_primary", "notes"]
        widgets = {
            "phone": forms.TextInput(
                attrs={"placeholder": "Ej.: +56 9 1234 5678", "inputmode": "tel"}
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": "Horario preferido, idioma, otra información de contacto.",
                }
            ),
        }
        labels = {
            "is_primary": "Es el contacto principal",
        }

    def clean_phone(self):
        value = (self.cleaned_data.get("phone") or "").strip()
        if not value:
            raise ValidationError("El teléfono es obligatorio.")
        if not re.fullmatch(r"[0-9+()\-\s.]{6,30}", value):
            raise ValidationError(
                "Usa solo números, espacios, paréntesis, puntos, guiones y el signo +."
            )
        if len(re.sub(r"\D", "", value)) < 6:
            raise ValidationError("Ingresa un teléfono con al menos 6 dígitos.")
        return value

    def clean_notes(self):
        value = (self.cleaned_data.get("notes") or "").strip()
        if len(value) > 500:
            raise ValidationError("Las notas no pueden superar los 500 caracteres.")
        return value
