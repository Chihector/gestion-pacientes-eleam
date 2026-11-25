import csv
import io
from datetime import datetime, time, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from accounts.models import Role
from audit.models import AuditLog
from incidents.models import Incident

pytestmark = pytest.mark.django_db


def incident_payload(resident, **overrides):
    payload = {
        "resident": resident.pk,
        "occurred_at": timezone.localtime().strftime("%Y-%m-%dT%H:%M"),
        "incident_type": Incident.Type.FALL,
        "location": "Baño de habitación 12",
        "severity": Incident.Severity.MINOR,
        "description": "La persona resbaló al caminar hacia el baño.",
        "actions_taken": "Se avisó a Enfermería y se acompañó a la persona.",
        "witnesses": "",
        "notified_to": "Enfermería de turno",
        "notify_family": False,
        "notify_direction": False,
    }
    payload.update(overrides)
    return payload


def make_incident(resident, reporter, **overrides):
    data = incident_payload(resident)
    data.update(
        {
            "occurred_at": timezone.now(),
            "resident": resident,
            "created_by": reporter,
            "updated_by": reporter,
        }
    )
    data.update(overrides)
    return Incident.objects.create(**data)


@pytest.mark.parametrize("role", [Role.ENFERMERA_JEFE, Role.ENFERMERIA, Role.TECNICO, Role.CUIDADOR])
def test_authorized_care_roles_can_report_incidents(
    client, make_user, resident, role
):
    user = make_user(f"{role.lower()}@example.test", role)
    client.force_login(user)

    response = client.post(
        reverse("incidents:create"), incident_payload(resident)
    )

    assert response.status_code == 302
    incident = Incident.objects.get()
    assert incident.resident == resident
    assert incident.created_by == user
    assert incident.status == Incident.Status.OPEN
    assert AuditLog.objects.filter(
        action=AuditLog.Action.CREATE,
        model_label="incidents.Incident",
        object_id=str(incident.pk),
        actor=user,
    ).exists()


@pytest.mark.parametrize("role", [Role.DIRECCION, Role.ADMINISTRACION, Role.MEDICO])
def test_only_care_roles_can_create_incidents(
    client, make_user, resident, role
):
    user = make_user(f"{role.lower()}@example.test", role)
    client.force_login(user)

    response = client.post(
        reverse("incidents:create"), incident_payload(resident)
    )

    assert response.status_code == 403
    assert Incident.objects.count() == 0


def test_incident_form_rejects_future_dates_and_short_descriptions(
    client, head_nurse_user, resident
):
    client.force_login(head_nurse_user)
    future = (timezone.localtime() + timedelta(days=1)).strftime(
        "%Y-%m-%dT%H:%M"
    )

    response = client.post(
        reverse("incidents:create"),
        incident_payload(resident, occurred_at=future, description="Caída"),
    )

    assert response.status_code == 200
    assert response.context["form"].errors["occurred_at"]
    assert response.context["form"].errors["description"]
    assert Incident.objects.count() == 0


def test_archived_resident_cannot_be_selected_for_new_incident(
    client, head_nurse_user, resident
):
    resident.is_active = False
    resident.save()
    client.force_login(head_nurse_user)

    response = client.post(
        reverse("incidents:create"), incident_payload(resident)
    )

    assert response.status_code == 200
    assert response.context["form"].errors["resident"]
    assert Incident.objects.count() == 0


def test_incident_list_is_forbidden_to_administration(
    client, admin_user, resident, head_nurse_user
):
    make_incident(resident, head_nurse_user)
    client.force_login(admin_user)

    response = client.get(reverse("incidents:list"))

    assert response.status_code == 403


@pytest.mark.parametrize("role", [Role.DIRECCION, Role.MEDICO, Role.ENFERMERA_JEFE])
def test_nursing_and_direction_can_close_with_audited_reason(
    client, make_user, resident, caregiver_user, role
):
    reviewer = make_user(f"{role.lower()}-review@example.test", role)
    incident = make_incident(resident, caregiver_user)
    client.force_login(reviewer)

    response = client.post(
        reverse("incidents:close", kwargs={"pk": incident.pk}),
        {"close_reason": "Se realizó seguimiento con el equipo de turno."},
    )

    assert response.status_code == 302
    incident.refresh_from_db()
    assert incident.status == Incident.Status.CLOSED
    assert incident.closed_by == reviewer
    assert incident.closed_at is not None
    assert incident.close_reason.startswith("Se realizó seguimiento")
    assert AuditLog.objects.filter(
        action=AuditLog.Action.CLOSE,
        model_label="incidents.Incident",
        object_id=str(incident.pk),
        actor=reviewer,
    ).exists()


def test_caregiver_cannot_close_incident(client, caregiver_user, resident):
    incident = make_incident(resident, caregiver_user)
    client.force_login(caregiver_user)

    response = client.post(
        reverse("incidents:close", kwargs={"pk": incident.pk}),
        {"close_reason": "Seguimiento realizado y documentado."},
    )

    assert response.status_code == 403
    incident.refresh_from_db()
    assert incident.status == Incident.Status.OPEN


def test_close_requires_a_reason(client, head_nurse_user, resident, caregiver_user):
    incident = make_incident(resident, caregiver_user)
    client.force_login(head_nurse_user)

    response = client.post(
        reverse("incidents:close", kwargs={"pk": incident.pk}),
        {"close_reason": "Cerrado"},
    )

    assert response.status_code == 302
    incident.refresh_from_db()
    assert incident.status == Incident.Status.OPEN
    assert not AuditLog.objects.filter(
        action=AuditLog.Action.CLOSE,
        model_label="incidents.Incident",
        object_id=str(incident.pk),
    ).exists()


def test_reports_are_restricted_and_count_only_selected_period(
    client, head_nurse_user, technician_user, resident
):
    today = timezone.localdate()
    current_time = timezone.make_aware(datetime.combine(today, time(12, 0)))
    old_date = today - timedelta(days=40)
    old_time = timezone.make_aware(datetime.combine(old_date, time(12, 0)))
    make_incident(resident, technician_user, occurred_at=current_time)
    make_incident(
        resident,
        technician_user,
        occurred_at=old_time,
        severity=Incident.Severity.SERIOUS,
    )
    client.force_login(head_nurse_user)

    response = client.get(reverse("incidents:reports"), {"desde": today.isoformat(), "hasta": today.isoformat()})

    assert response.status_code == 200
    assert response.context["total_count"] == 1
    assert response.context["open_count"] == 1
    assert response.context["closed_count"] == 0


def test_non_report_roles_cannot_access_incident_reports(
    client, caregiver_user
):
    client.force_login(caregiver_user)

    assert client.get(reverse("incidents:reports")).status_code == 403


def test_invalid_incident_list_filters_do_not_show_unfiltered_data(
    client, head_nurse_user, caregiver_user, resident
):
    make_incident(resident, caregiver_user)
    client.force_login(head_nurse_user)

    response = client.get(
        reverse("incidents:list"),
        {"desde": "2026-10-30", "hasta": "2026-10-01"},
    )

    assert response.status_code == 200
    assert response.context["paginator"].count == 0
    assert response.context["filter_form"].errors


def test_administration_cannot_read_incident_audit_payload(
    client, admin_user, direction_user, resident, caregiver_user
):
    incident = make_incident(resident, caregiver_user)
    client.force_login(admin_user)

    admin_response = client.get(reverse("audit:list"))

    assert admin_response.status_code == 200
    assert all(
        log.model_label != "incidents.Incident"
        for log in admin_response.context["logs"]
    )

    client.force_login(direction_user)
    direction_response = client.get(reverse("audit:list"))
    assert any(
        log.model_label == "incidents.Incident"
        and log.object_id == str(incident.pk)
        for log in direction_response.context["logs"]
    )

    client.force_login(admin_user)
    dashboard_response = client.get(reverse("core:dashboard"))
    assert dashboard_response.status_code == 200
    assert all(
        log.model_label != "incidents.Incident"
        for log in dashboard_response.context["recent_logs"]
    )


# --- Exportación CSV de incidentes ------------------------------------------


@pytest.mark.parametrize(
    "role,expected",
    [
        (Role.DIRECCION, 200),
        (Role.MEDICO, 200),
        (Role.ENFERMERA_JEFE, 200),
        (Role.ADMINISTRACION, 403),
        (Role.ENFERMERIA, 403),
        (Role.TECNICO, 403),
        (Role.CUIDADOR, 403),
    ],
)
def test_incident_export_is_limited_to_report_roles(
    client, make_user, resident, caregiver_user, role, expected
):
    user = make_user(f"export-{role.lower()}@example.test", role)
    make_incident(resident, caregiver_user)
    client.force_login(user)

    response = client.get(reverse("incidents:export"))

    assert response.status_code == expected
    if expected == 200:
        assert response["Content-Type"].startswith("text/csv")
        assert "attachment;" in response["Content-Disposition"]


def test_incident_export_applies_filters_and_is_audited(
    client, direction_user, caregiver_user, resident
):
    today = timezone.localdate()
    make_incident(
        resident,
        caregiver_user,
        occurred_at=timezone.make_aware(datetime.combine(today, time(12, 0))),
        description="Incidente reciente",
        notified_to="Enfermería de turno",
    )
    make_incident(
        resident,
        caregiver_user,
        occurred_at=timezone.make_aware(
            datetime.combine(today - timedelta(days=40), time(12, 0))
        ),
        description="Incidente antiguo",
    )
    client.force_login(direction_user)

    response = client.get(
        reverse("incidents:export"),
        {"desde": today.isoformat(), "hasta": today.isoformat()},
    )

    assert response.status_code == 200
    content = response.content.decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(content)))
    assert len(rows) == 2  # cabecera + un registro
    assert rows[0][10] == "Notificaciones realizadas"
    assert "Incidente reciente" in content
    assert "Incidente antiguo" not in content
    assert "Enfermería de turno" in content

    log = AuditLog.objects.get(
        action=AuditLog.Action.EXPORT,
        model_label="incidents.Incident",
    )
    assert log.actor == direction_user
    assert log.changes["total"] == 1
    assert log.changes["filtros"]["desde"] == today.isoformat()
