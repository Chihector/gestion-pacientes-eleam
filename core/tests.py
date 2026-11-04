from __future__ import annotations

from datetime import date

import pytest
from django.urls import reverse

from residents.models import Contact, Resident

pytestmark = pytest.mark.django_db


def test_health_check_responds_ok_without_auth(client):
    response = client.get(reverse("core:health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_requires_login(client):
    response = client.get(reverse("core:dashboard"))
    assert response.status_code == 302
    assert reverse("accounts:login") in response["Location"]


def test_dashboard_counts_active_allergies_and_missing_contacts(
    client, nurse_user, resident
):
    second = Resident.objects.create(
        first_name="Sin",
        last_name="Contacto",
        rut="12345678-5",
        birth_date=date(1940, 1, 1),
        admission_date=date(2024, 1, 1),
        allergies="",
    )
    Resident.objects.create(
        first_name="Ficha",
        last_name="Archivada",
        rut="15678901-1",
        birth_date=date(1940, 1, 1),
        admission_date=date(2024, 1, 1),
        allergies="Sulfas",
        is_active=False,
    )
    Contact.objects.create(
        resident=resident,
        name="Contacto Principal",
        relationship="Hija",
        phone="+56 9 0000 0000",
        is_primary=True,
    )
    client.force_login(nurse_user)

    response = client.get(reverse("core:dashboard"))
    context = response.context

    assert response.status_code == 200
    assert context["active_count"] == 2
    assert context["allergy_count"] == 1
    assert context["archived_count"] == 1
    assert context["missing_contact_count"] == 1
    assert second in list(context["missing_contact_residents"])
    assert context["greeting_name"] == "Persona"


def test_dashboard_hides_audit_activity_from_nurse(client, nurse_user):
    client.force_login(nurse_user)
    response = client.get(reverse("core:dashboard"))

    assert "recent_logs" not in response.context


def test_dashboard_shows_audit_activity_to_direction(client, direction_user):
    client.force_login(direction_user)
    response = client.get(reverse("core:dashboard"))

    assert "recent_logs" in response.context
    assert response.templates[0].name == "core/dashboard.html"
