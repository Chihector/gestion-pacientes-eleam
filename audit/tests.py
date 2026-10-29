from __future__ import annotations

import pytest
from django.urls import reverse

from audit.models import AuditLog
from residents.models import Resident

pytestmark = pytest.mark.django_db


def _clinical_payload(**overrides):
    payload = {
        "allergies": "Penicilina, látex",
        "relevant_background": "Hipertensión arterial.",
        "clinical_notes": "Camina con apoyo.",
    }
    payload.update(overrides)
    return payload


def test_create_log_has_actor_and_ip(client, nurse_user):
    client.force_login(nurse_user)
    response = client.post(
        reverse("residents:create"),
        {
            "first_name": "Auditada",
            "last_name": "Ficticia",
            "rut": "12.345.678-5",
            "birth_date": "1940-01-01",
            "sex": Resident.Sex.FEMENINO,
            "admission_date": "2024-01-01",
            "status": Resident.Status.ACTIVO,
            "health_insurance": Resident.HealthInsurance.FONASA,
        },
        REMOTE_ADDR="190.12.34.56",
    )

    assert response.status_code == 302
    log = AuditLog.objects.get(
        action=AuditLog.Action.CREATE,
        model_label="residents.Resident",
    )
    assert log.actor == nurse_user
    assert log.ip_address == "190.12.34.56"
    assert log.changes["first_name"]["after"] == "Auditada"


def test_update_log_stores_before_and_after(client, nurse_user, resident):
    client.force_login(nurse_user)
    response = client.post(
        reverse("residents:clinical_update", args=[resident.pk]),
        _clinical_payload(),
    )

    assert response.status_code == 302
    resident.refresh_from_db()
    log = AuditLog.objects.get(
        action=AuditLog.Action.UPDATE,
        model_label="residents.Resident",
        object_id=str(resident.pk),
    )
    assert log.changes["allergies"]["before"] == "Penicilina"
    assert log.changes["allergies"]["after"] == "Penicilina, látex"
    assert log.changes["allergies"]["label"] == "alergias"


def test_password_is_never_in_audit_changes(client, nurse_user):
    client.force_login(nurse_user)
    client.post(
        reverse("accounts:password_change"),
        {
            "old_password": "ClaveSegura2026!",
            "new_password1": "OtraClave2026!",
            "new_password2": "OtraClave2026!",
        },
    )

    log = AuditLog.objects.get(action=AuditLog.Action.PASSWORD)
    assert log.changes == {}
    assert "ClaveSegura2026!" not in str(log.changes)
    assert "OtraClave2026!" not in str(log.changes)


def test_audit_list_only_for_direction_and_administration(
    client, direction_user, admin_user, nurse_user
):
    client.force_login(direction_user)
    assert client.get(reverse("audit:list")).status_code == 200

    client.force_login(admin_user)
    assert client.get(reverse("audit:list")).status_code == 200

    client.force_login(nurse_user)
    assert client.get(reverse("audit:list")).status_code == 403


def test_audit_list_filters_by_action_and_model(client, direction_user):
    AuditLog.objects.create(
        actor=direction_user,
        actor_repr=str(direction_user),
        action=AuditLog.Action.CREATE,
        model_label="residents.Resident",
        object_id="1",
        object_repr="Rosa Ficticia",
    )
    AuditLog.objects.create(
        actor=direction_user,
        actor_repr=str(direction_user),
        action=AuditLog.Action.DELETE,
        model_label="residents.Contact",
        object_id="3",
        object_repr="María Ficticia",
    )
    client.force_login(direction_user)

    response = client.get(reverse("audit:list"), {"accion": AuditLog.Action.DELETE})
    assert response.context["paginator"].count == 1
    assert response.context["logs"][0].object_repr == "María Ficticia"

    response = client.get(reverse("audit:list"), {"modelo": "residents.Resident"})
    assert response.context["paginator"].count == 1
    assert response.context["logs"][0].object_repr == "Rosa Ficticia"


def test_audit_list_search_by_actor(client, direction_user):
    AuditLog.objects.create(
        actor=direction_user,
        actor_repr=f"Daniela Demo <{direction_user.email}>",
        action=AuditLog.Action.CREATE,
        model_label="residents.Resident",
        object_id="1",
        object_repr="Rosa Ficticia",
    )
    client.force_login(direction_user)

    response = client.get(reverse("audit:list"), {"q": "Daniela"})
    assert response.context["paginator"].count == 1
