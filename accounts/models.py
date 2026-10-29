from __future__ import annotations

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models import Q

from core.models import TimeStampedModel


class Role(models.TextChoices):
    DIRECCION = "DIRECCION", "Dirección"
    ENFERMERIA = "ENFERMERIA", "Enfermería"
    TECNICO = "TECNICO", "Técnico/a"
    CUIDADOR = "CUIDADOR", "Cuidador/a"
    ADMINISTRACION = "ADMINISTRACION", "Administración"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio.")
        email = self.normalize_email(email).strip().lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Role.ADMINISTRACION)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Un superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superusuario debe tener is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    email = models.EmailField("correo electrónico", unique=True)
    first_name = models.CharField("nombre", max_length=150)
    last_name = models.CharField("apellidos", max_length=150)
    role = models.CharField(
        "rol", max_length=20, choices=Role.choices, default=Role.CUIDADOR
    )
    is_staff = models.BooleanField(
        "acceso al admin técnico",
        default=False,
        help_text="Solo para administración técnica del sistema.",
    )
    is_active = models.BooleanField("activo", default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        ordering = ["last_name", "first_name", "email"]

    def __str__(self) -> str:
        return self.get_full_name() or self.email

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        return self.first_name

    @property
    def initials(self) -> str:
        initials = f"{self.first_name[:1]}{self.last_name[:1]}".upper()
        return initials or self.email[:2].upper()

    @property
    def can_manage_users(self) -> bool:
        return self.is_superuser or self.role == Role.ADMINISTRACION

    @property
    def can_view_audit(self) -> bool:
        return self.is_superuser or self.role in {Role.DIRECCION, Role.ADMINISTRACION}

    @property
    def can_edit_resident_admin(self) -> bool:
        return self.is_superuser or self.role in {Role.ENFERMERIA, Role.ADMINISTRACION}

    @property
    def can_edit_resident_clinical(self) -> bool:
        return self.is_superuser or self.role == Role.ENFERMERIA

    @property
    def can_manage_contacts(self) -> bool:
        return self.is_superuser or self.role in {Role.ENFERMERIA, Role.ADMINISTRACION}

    @property
    def can_archive_residents(self) -> bool:
        return self.is_superuser or self.role in {Role.ENFERMERIA, Role.ADMINISTRACION}

    @property
    def can_view_residents(self) -> bool:
        return True


def active_admin_count(exclude_pk: int | None = None) -> int:
    queryset = User.objects.filter(is_active=True).filter(
        Q(role=Role.ADMINISTRACION) | Q(is_superuser=True)
    )
    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)
    return queryset.count()
