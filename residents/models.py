from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse

from audit.models import AuditedModel

from .rut import clean_rut, rut_display, validate_rut


class Resident(AuditedModel):
    class Sex(models.TextChoices):
        FEMENINO = "F", "Femenino"
        MASCULINO = "M", "Masculino"
        OTRO = "OTRO", "Otro"
        NO_INFORMA = "NO_INFORMA", "No informa"

    class Status(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        HOSPITALIZADO = "HOSPITALIZADO", "Hospitalizado"
        EGRESADO = "EGRESADO", "Egresado"
        FALLECIDO = "FALLECIDO", "Fallecido"

    class HealthInsurance(models.TextChoices):
        FONASA = "FONASA", "FONASA"
        ISAPRE = "ISAPRE", "ISAPRE"
        PARTICULAR = "PARTICULAR", "Particular"
        OTRA = "OTRA", "Otra"
        NO_INFORMA = "NO_INFORMA", "No informa"

    is_demo = models.BooleanField(
        "dato de demostración",
        default=False,
        help_text="Marca las fichas ficticias. No usar en producción.",
    )
    first_name = models.CharField("nombre", max_length=100)
    last_name = models.CharField("apellidos", max_length=150)
    preferred_name = models.CharField(
        "nombre preferido", max_length=80, blank=True
    )
    rut = models.CharField("RUT", max_length=12, unique=True)
    birth_date = models.DateField("fecha de nacimiento")
    sex = models.CharField(
        "sexo registrado",
        max_length=10,
        choices=Sex.choices,
        default=Sex.NO_INFORMA,
    )
    room = models.CharField("habitación", max_length=20, blank=True)
    admission_date = models.DateField("fecha de ingreso")
    status = models.CharField(
        "estado", max_length=20, choices=Status.choices, default=Status.ACTIVO
    )
    health_insurance = models.CharField(
        "previsión",
        max_length=20,
        choices=HealthInsurance.choices,
        default=HealthInsurance.NO_INFORMA,
    )
    allergies = models.TextField(
        "alergias",
        blank=True,
        help_text="Vacío significa 'no registradas', no 'sin alergias'.",
    )
    relevant_background = models.TextField("antecedentes relevantes", blank=True)
    clinical_notes = models.TextField("observaciones para el cuidado", blank=True)
    is_active = models.BooleanField(
        "ficha activa",
        default=True,
        help_text="Al desmarcar se archiva; no se elimina la ficha.",
    )

    class Meta:
        verbose_name = "residente"
        verbose_name_plural = "residentes"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["is_active", "status"]),
            models.Index(fields=["last_name", "first_name"]),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def clean(self):
        super().clean()
        self.rut = clean_rut(self.rut)
        errors = {}
        if self.rut and not validate_rut(self.rut):
            errors["rut"] = "Ingresa un RUT válido con dígito verificador."
        if self.birth_date and self.birth_date > date.today():
            errors["birth_date"] = "La fecha de nacimiento no puede ser futura."
        if self.admission_date and self.admission_date > date.today():
            errors["admission_date"] = "La fecha de ingreso no puede ser futura."
        if (
            self.birth_date
            and self.admission_date
            and self.admission_date < self.birth_date
        ):
            errors["admission_date"] = (
                "La fecha de ingreso no puede ser anterior al nacimiento."
            )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.rut = clean_rut(self.rut)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("residents:detail", kwargs={"pk": self.pk})

    @property
    def full_name(self) -> str:
        return str(self)

    @property
    def rut_formatted(self) -> str:
        return rut_display(self.rut)

    @property
    def age(self) -> int | None:
        if not self.birth_date:
            return None
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    @property
    def initials(self) -> str:
        return f"{self.first_name[:1]}{self.last_name[:1]}".upper()

    @property
    def has_allergies(self) -> bool:
        return bool(self.allergies.strip())

    @property
    def is_archived(self) -> bool:
        return not self.is_active


class Contact(AuditedModel):
    resident = models.ForeignKey(
        Resident,
        verbose_name="residente",
        related_name="contacts",
        on_delete=models.CASCADE,
    )
    name = models.CharField("nombre completo", max_length=150)
    relationship = models.CharField("parentesco o vínculo", max_length=80)
    phone = models.CharField("teléfono", max_length=30)
    email = models.EmailField("correo electrónico", blank=True)
    is_primary = models.BooleanField(
        "contacto principal",
        default=False,
        help_text="Solo puede haber uno por residente.",
    )
    notes = models.TextField("notas de contacto", blank=True)

    class Meta:
        verbose_name = "contacto"
        verbose_name_plural = "contactos"
        ordering = ["-is_primary", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["resident"],
                condition=Q(is_primary=True),
                name="unique_primary_contact_per_resident",
            )
        ]
        indexes = [models.Index(fields=["resident", "is_primary"])]

    def __str__(self) -> str:
        return f"{self.name} · {self.resident}"

    def save(self, *args, **kwargs):
        if self.is_primary and self.resident_id:
            others = Contact.objects.filter(
                resident_id=self.resident_id, is_primary=True
            ).exclude(pk=self.pk)
            for other in others:
                other.is_primary = False
                other.save()
        super().save(*args, **kwargs)


class Disease(AuditedModel):
    """Enfermedad, diagnóstico o patología de un residente."""

    class Status(models.TextChoices):
        ACTIVA = "ACTIVA", "Activa"
        CONTROLADA = "CONTROLADA", "Controlada"
        EN_TRATAMIENTO = "EN_TRATAMIENTO", "En tratamiento"
        RESUELTA = "RESUELTA", "Resuelta / Inactiva"

    resident = models.ForeignKey(
        Resident,
        verbose_name="residente",
        related_name="diseases",
        on_delete=models.CASCADE,
    )
    name = models.CharField("enfermedad o condición", max_length=150)
    diagnosed_date = models.DateField(
        "fecha de diagnóstico", null=True, blank=True
    )
    status = models.CharField(
        "estado",
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVA,
    )
    notes = models.TextField("observaciones / indicaciones", blank=True)

    class Meta:
        verbose_name = "enfermedad o condición"
        verbose_name_plural = "enfermedades y condiciones"
        ordering = ["status", "name"]
        indexes = [
            models.Index(fields=["resident", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} · {self.resident}"

    @property
    def is_active_condition(self) -> bool:
        return self.status != self.Status.RESUELTA

    @property
    def status_css(self) -> str:
        return {
            self.Status.ACTIVA: "danger",
            self.Status.EN_TRATAMIENTO: "warning",
            self.Status.CONTROLADA: "info",
            self.Status.RESUELTA: "muted",
        }.get(self.status, "muted")


class Medication(AuditedModel):
    """Medicamento o remedio prescrito para un residente."""

    class Status(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        SOS = "SOS", "SOS (condicional)"
        SUSPENDIDO = "SUSPENDIDO", "Suspendido"
        FINALIZADO = "FINALIZADO", "Finalizado"

    class Route(models.TextChoices):
        ORAL = "ORAL", "Oral"
        SUBLINGUAL = "SUBLINGUAL", "Sublingual"
        SUBCUTANEA = "SUBCUTANEA", "Subcutánea"
        INTRAMUSCULAR = "INTRAMUSCULAR", "Intramuscular"
        TOPICA = "TOPICA", "Tópica"
        OFTALMICA = "OFTALMICA", "Oftálmica"
        OTICA = "OTICA", "Ótica"
        INHALATORIA = "INHALATORIA", "Inhalatoria"
        RECTAL = "RECTAL", "Rectal"
        OTRA = "OTRA", "Otra"

    resident = models.ForeignKey(
        Resident,
        verbose_name="residente",
        related_name="medications",
        on_delete=models.CASCADE,
    )
    name = models.CharField("nombre del medicamento", max_length=150)
    dose = models.CharField(
        "dosis",
        max_length=100,
        help_text="Ej.: 50 mg, 1 comprimido, 10 UI, 5 ml",
    )
    frequency = models.CharField(
        "frecuencia u horario",
        max_length=120,
        help_text="Ej.: Cada 8 hrs, 08:00 y 20:00, Con el desayuno, SOS en caso de dolor",
    )
    route = models.CharField(
        "vía de administración",
        max_length=20,
        choices=Route.choices,
        default=Route.ORAL,
    )
    status = models.CharField(
        "estado del tratamiento",
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVO,
    )
    prescribed_by = models.CharField(
        "profesional que indica",
        max_length=150,
        blank=True,
        help_text="Médico tratante o especialista que prescribe.",
    )
    start_date = models.DateField(
        "fecha de inicio",
        null=True,
        blank=True,
    )
    end_date = models.DateField(
        "fecha de término",
        null=True,
        blank=True,
    )
    instructions = models.TextField(
        "indicaciones especiales",
        blank=True,
        help_text="Instrucciones para la administración (ej. tomar en ayunas, con las comidas, etc.).",
    )
    notes = models.TextField("observaciones", blank=True)

    class Meta:
        verbose_name = "medicamento"
        verbose_name_plural = "medicamentos"
        ordering = ["status", "name"]
        indexes = [
            models.Index(fields=["resident", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} {self.dose} · {self.resident}"

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {"end_date": "La fecha de término no puede ser anterior a la de inicio."}
            )

    @property
    def is_current(self) -> bool:
        return self.status in {self.Status.ACTIVO, self.Status.SOS}

    @property
    def status_css(self) -> str:
        return {
            self.Status.ACTIVO: "success",
            self.Status.SOS: "warning",
            self.Status.SUSPENDIDO: "danger",
            self.Status.FINALIZADO: "muted",
        }.get(self.status, "muted")
