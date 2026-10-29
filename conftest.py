from __future__ import annotations

from datetime import date

import pytest

from accounts.models import Role, User
from residents.models import Resident


@pytest.fixture(autouse=True)
def fast_password_hasher(settings):
    """Evita gastar segundos por cada usuario creado en la suite."""

    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture
def make_user(db):
    def _make_user(email: str, role: str, **extra):
        extra.setdefault("first_name", "Persona")
        extra.setdefault("last_name", "Demo")
        return User.objects.create_user(
            email=email, password="ClaveSegura2026!", role=role, **extra
        )

    return _make_user


@pytest.fixture
def admin_user(make_user):
    return make_user("administracion@example.test", Role.ADMINISTRACION)


@pytest.fixture
def direction_user(make_user):
    return make_user("direccion@example.test", Role.DIRECCION)


@pytest.fixture
def nurse_user(make_user):
    return make_user("enfermeria@example.test", Role.ENFERMERIA)


@pytest.fixture
def technician_user(make_user):
    return make_user("tecnico@example.test", Role.TECNICO)


@pytest.fixture
def caregiver_user(make_user):
    return make_user("cuidador@example.test", Role.CUIDADOR)


@pytest.fixture
def resident(db):
    return Resident.objects.create(
        first_name="Rosa",
        last_name="Ficticia Pérez",
        preferred_name="Rosita",
        rut="11222333-9",
        birth_date=date(1942, 3, 12),
        sex=Resident.Sex.FEMENINO,
        room="12",
        admission_date=date(2023, 6, 14),
        status=Resident.Status.ACTIVO,
        health_insurance=Resident.HealthInsurance.FONASA,
        allergies="Penicilina",
        relevant_background="Hipertensión arterial.",
        clinical_notes="Camina con apoyo.",
        is_demo=True,
    )
