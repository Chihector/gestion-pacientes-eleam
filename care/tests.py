from __future__ import annotations

from datetime import date, timedelta

import pytest
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from accounts.models import Role
from audit.models import AuditLog
from care.models import CarePlan, DailyCareRecord
from residents.models import Resident
from residents.rut import calculate_dv

pytestmark = pytest.mark.django_db


def make_record(resident, user, **overrides):
    now = timezone.localtime().replace(second=0, microsecond=0)
    data = {
        "resident": resident,
        "recorded_at": now,
        "shift": DailyCareRecord.Shift.MANANA,
        "category": DailyCareRecord.Category.ALIMENTACION,
        "description": "Desayuno completo; aceptó toda la ración.",
        "observations": "",
        "created_by": user,
        "updated_by": user,
    }
    data.update(overrides)
    return DailyCareRecord.objects.create(**data)


def make_plan(resident, user, **overrides):
    data = {
        "resident": resident,
        "title": "Riesgo de caídas",
        "need": "Se levanta de noche sin apoyo.",
        "objective": "Mantener desplazamientos seguros.",
        "actions": "Acompañar al baño y dejar el timbre al alcance.",
        "responsible": user,
        "start_date": timezone.localdate(),
        "review_date": timezone.localdate() + timedelta(days=7),
        "created_by": user,
        "updated_by": user,
    }
    data.update(overrides)
    return CarePlan.objects.create(**data)


def form_payload(resident, **overrides):
    payload = {
        "resident": resident.pk,
        "care_plan": "",
        "recorded_at": timezone.localtime().strftime("%Y-%m-%dT%H:%M"),
        "shift": DailyCareRecord.Shift.MANANA,
        "category": DailyCareRecord.Category.ALIMENTACION,
        "description": "Desayuno completo; aceptó toda la ración.",
        "observations": "",
    }
    payload.update(overrides)
    return payload


# --- Permisos de registro ---------------------------------------------------


def test_anonymous_user_is_redirected_from_care_list(client):
    response = client.get(reverse("care:record_list"))
    assert response.status_code == 302
    assert reverse("accounts:login") in response["Location"]


@pytest.mark.parametrize(
    "role", [Role.ENFERMERA_JEFE, Role.ENFERMERIA, Role.TECNICO, Role.CUIDADOR]
)
def test_care_roles_can_create_record(client, make_user, resident, role):
    user = make_user(f"{role.lower()}@example.test", role)
    client.force_login(user)

    response = client.post(
        reverse("care:record_create"), form_payload(resident)
    )

    assert response.status_code == 302
    record = DailyCareRecord.objects.get()
    assert record.resident == resident
    assert record.created_by == user
    assert record.updated_by == user
    log = AuditLog.objects.get(
        action=AuditLog.Action.CREATE,
        model_label="care.DailyCareRecord",
        object_id=str(record.pk),
    )
    assert log.actor == user


@pytest.mark.parametrize("role", [Role.ADMINISTRACION, Role.DIRECCION, Role.MEDICO])
def test_roles_without_care_permission_cannot_create(
    client, make_user, resident, role
):
    user = make_user(f"{role.lower()}@example.test", role)
    client.force_login(user)

    response = client.post(
        reverse("care:record_create"), form_payload(resident)
    )

    assert response.status_code == 403
    assert DailyCareRecord.objects.count() == 0


def test_record_rejects_future_date(client, head_nurse_user, resident):
    client.force_login(head_nurse_user)
    future = (timezone.localtime() + timedelta(days=1)).strftime(
        "%Y-%m-%dT%H:%M"
    )

    response = client.post(
        reverse("care:record_create"),
        form_payload(resident, recorded_at=future),
    )

    assert response.status_code == 200
    assert "futura" in response.context["form"].errors["recorded_at"][0]
    assert DailyCareRecord.objects.count() == 0


def test_record_rejects_plan_from_another_resident(
    client, head_nurse_user, resident
):
    other = Resident.objects.create(
        first_name="Otro",
        last_name="Ficticio",
        rut=f"15678901-{calculate_dv('15678901')}",
        birth_date=date(1950, 1, 1),
        admission_date=date(2023, 1, 1),
    )
    plan = make_plan(other, head_nurse_user)
    client.force_login(head_nurse_user)

    response = client.post(
        reverse("care:record_create"),
        form_payload(resident, care_plan=plan.pk),
    )

    assert response.status_code == 200
    assert "otro residente" in response.context["form"].errors["care_plan"][0]
    assert DailyCareRecord.objects.count() == 0


def test_save_and_register_another_returns_to_form(
    client, caregiver_user, resident
):
    client.force_login(caregiver_user)

    response = client.post(
        reverse("care:record_create"),
        form_payload(resident, save_and_new="1"),
    )

    assert response.status_code == 302
    assert response["Location"].startswith(reverse("care:record_create"))
    assert f"residente={resident.pk}" in response["Location"]


# --- Revisión de Enfermería -------------------------------------------------


def test_head_nurse_can_review_record(client, head_nurse_user, caregiver_user, resident):
    record = make_record(
        resident, caregiver_user, requires_nursing_review=True
    )
    client.force_login(head_nurse_user)

    response = client.post(
        reverse("care:record_review", kwargs={"pk": record.pk}),
        {"review_notes": "Se verificó con el turno; información correcta."},
    )

    assert response.status_code == 302
    record.refresh_from_db()
    assert record.reviewed_by == head_nurse_user
    assert record.reviewed_at is not None
    assert "correcta" in record.review_notes
    assert record.review_pending is False
    log = AuditLog.objects.get(
        action=AuditLog.Action.REVIEW,
        model_label="care.DailyCareRecord",
        object_id=str(record.pk),
    )
    assert log.actor == head_nurse_user


def test_non_head_nurse_cannot_review_record(
    client, caregiver_user, resident
):
    record = make_record(
        resident, caregiver_user, requires_nursing_review=True
    )
    client.force_login(caregiver_user)

    response = client.post(
        reverse("care:record_review", kwargs={"pk": record.pk}),
        {"review_notes": "Intento no autorizado."},
    )

    assert response.status_code == 403
    record.refresh_from_db()
    assert record.reviewed_at is None


def test_record_without_review_flag_cannot_be_reviewed(
    client, head_nurse_user, caregiver_user, resident
):
    record = make_record(resident, caregiver_user)
    client.force_login(head_nurse_user)

    response = client.post(
        reverse("care:record_review", kwargs={"pk": record.pk}), {}
    )

    assert response.status_code == 302
    record.refresh_from_db()
    assert record.reviewed_at is None
    assert record.can_be_reviewed_by(head_nurse_user) is False


def test_corrected_record_cannot_be_reviewed(
    client, head_nurse_user, caregiver_user, resident
):
    record = make_record(
        resident,
        caregiver_user,
        status=DailyCareRecord.Status.CORREGIDO,
        requires_nursing_review=True,
    )
    client.force_login(head_nurse_user)

    response = client.post(
        reverse("care:record_review", kwargs={"pk": record.pk}), {}
    )

    assert response.status_code == 302
    record.refresh_from_db()
    assert record.reviewed_at is None


# --- Correcciones -----------------------------------------------------------


def test_correction_preserves_original_and_is_audited(
    client, caregiver_user, resident
):
    original = make_record(resident, caregiver_user)
    client.force_login(caregiver_user)

    response = client.post(
        reverse("care:record_correct", kwargs={"pk": original.pk}),
        {
            "recorded_at": timezone.localtime(original.recorded_at).strftime(
                "%Y-%m-%dT%H:%M"
            ),
            "shift": original.shift,
            "category": original.category,
            "description": "Desayuno completo; aceptó el 75% de la ración.",
            "observations": "Se corrigió la cantidad observada.",
            "correction_reason": "Se registró mal la cantidad de alimento.",
        },
    )

    assert response.status_code == 302
    assert DailyCareRecord.objects.count() == 2

    original.refresh_from_db()
    correction = DailyCareRecord.objects.get(supersedes=original)
    assert original.status == DailyCareRecord.Status.CORREGIDO
    assert correction.status == DailyCareRecord.Status.VIGENTE
    assert correction.resident == resident
    assert correction.created_by == caregiver_user
    assert correction.correction_reason.startswith("Se registró mal")
    assert "75%" in correction.description

    log = AuditLog.objects.get(
        action=AuditLog.Action.CORRECTION,
        model_label="care.DailyCareRecord",
        object_id=str(original.pk),
    )
    assert log.actor == caregiver_user


def test_correction_requires_reason(
    client, caregiver_user, resident
):
    original = make_record(resident, caregiver_user)
    client.force_login(caregiver_user)

    response = client.post(
        reverse("care:record_correct", kwargs={"pk": original.pk}),
        {
            "recorded_at": timezone.localtime(original.recorded_at).strftime(
                "%Y-%m-%dT%H:%M"
            ),
            "shift": original.shift,
            "category": original.category,
            "description": "Descripción corregida del cuidado.",
            "observations": "",
            "correction_reason": "",
        },
    )

    assert response.status_code == 200
    assert "correction_reason" in response.context["form"].errors
    assert DailyCareRecord.objects.count() == 1
    original.refresh_from_db()
    assert original.status == DailyCareRecord.Status.VIGENTE


def test_another_caregiver_cannot_correct_but_head_nurse_can(
    client, make_user, caregiver_user, head_nurse_user, resident
):
    original = make_record(resident, caregiver_user)
    other = make_user("otro.cuidador@example.test", Role.CUIDADOR)
    client.force_login(other)

    denied = client.get(
        reverse("care:record_correct", kwargs={"pk": original.pk})
    )
    assert denied.status_code == 403

    client.force_login(head_nurse_user)
    allowed = client.get(
        reverse("care:record_correct", kwargs={"pk": original.pk})
    )
    assert allowed.status_code == 200


def test_corrected_record_cannot_be_corrected_again(
    client, caregiver_user, resident
):
    original = make_record(
        resident, caregiver_user, status=DailyCareRecord.Status.CORREGIDO
    )
    client.force_login(caregiver_user)

    response = client.get(
        reverse("care:record_correct", kwargs={"pk": original.pk})
    )

    assert response.status_code == 302
    assert DailyCareRecord.objects.count() == 1


# --- Listado y detalle ------------------------------------------------------


def test_list_filters_and_hides_corrected_by_default(
    client, head_nurse_user, caregiver_user, resident
):
    current = make_record(resident, caregiver_user)
    corrected = make_record(
        resident,
        caregiver_user,
        status=DailyCareRecord.Status.CORREGIDO,
        category=DailyCareRecord.Category.MOVILIDAD,
    )
    client.force_login(head_nurse_user)

    response = client.get(reverse("care:record_list"))
    records = list(response.context["records"])
    assert current in records
    assert corrected not in records

    response = client.get(reverse("care:record_list"), {"corregidos": "1"})
    records = list(response.context["records"])
    assert corrected in records

    response = client.get(
        reverse("care:record_list"), {"turno": DailyCareRecord.Shift.TARDE}
    )
    assert list(response.context["records"]) == []


def test_list_filters_pending_review_and_resident(
    client, head_nurse_user, caregiver_user, resident
):
    pending = make_record(
        resident, caregiver_user, requires_nursing_review=True
    )
    make_record(resident, caregiver_user)
    client.force_login(head_nurse_user)

    response = client.get(
        reverse("care:record_list"), {"pendientes": "1"}
    )
    assert list(response.context["records"]) == [pending]

    response = client.get(
        reverse("care:record_list"),
        {"residente": resident.pk, "todas": "1"},
    )
    assert response.status_code == 200
    assert response.context["show_all_dates"] is True


def test_record_detail_shows_correction_chain(
    client, head_nurse_user, caregiver_user, resident
):
    original = make_record(resident, caregiver_user)
    correction = make_record(
        resident,
        caregiver_user,
        supersedes=original,
        correction_reason="Se corrigió la cantidad.",
        description="Descripción corregida del cuidado.",
    )
    original.status = DailyCareRecord.Status.CORREGIDO
    original.save(update_fields=["status"])
    client.force_login(head_nurse_user)

    response = client.get(original.get_absolute_url())
    assert response.status_code == 200
    assert "Este registro fue corregido" in response.content.decode()
    assert correction.get_absolute_url() in response.content.decode()

    response = client.get(correction.get_absolute_url())
    assert response.status_code == 200
    assert "Esta versión corrige" in response.content.decode()


# --- Planes de cuidados -----------------------------------------------------


def test_only_nurse_can_manage_care_plans(
    client, head_nurse_user, technician_user, resident
):
    client.force_login(technician_user)
    denied = client.post(
        reverse("care:plan_create", kwargs={"resident_pk": resident.pk}),
        {
            "title": "Riesgo de caídas",
            "need": "Se levanta de noche.",
            "objective": "Evitar caídas.",
            "actions": "Acompañar al baño.",
            "start_date": timezone.localdate().isoformat(),
            "review_date": (timezone.localdate() + timedelta(days=7)).isoformat(),
        },
    )
    assert denied.status_code == 403

    client.force_login(head_nurse_user)
    allowed = client.post(
        reverse("care:plan_create", kwargs={"resident_pk": resident.pk}),
        {
            "title": "Riesgo de caídas",
            "need": "Se levanta de noche.",
            "objective": "Evitar caídas.",
            "actions": "Acompañar al baño.",
            "start_date": timezone.localdate().isoformat(),
            "review_date": (timezone.localdate() + timedelta(days=7)).isoformat(),
        },
    )
    assert allowed.status_code == 302
    plan = CarePlan.objects.get()
    assert plan.resident == resident
    assert plan.created_by == head_nurse_user


def test_plan_close_requires_reason_and_can_reopen(
    client, head_nurse_user, resident
):
    plan = make_plan(resident, head_nurse_user)
    client.force_login(head_nurse_user)

    response = client.post(
        reverse("care:plan_close", kwargs={"pk": plan.pk}),
        {"closure_reason": "corto"},
    )
    assert response.status_code == 302
    plan.refresh_from_db()
    assert plan.status == CarePlan.Status.ACTIVO

    response = client.post(
        reverse("care:plan_close", kwargs={"pk": plan.pk}),
        {"closure_reason": "Objetivo alcanzado; se acuerda nuevo plan."},
    )
    assert response.status_code == 302
    plan.refresh_from_db()
    assert plan.status == CarePlan.Status.CERRADO
    assert plan.closure_reason.startswith("Objetivo alcanzado")
    log = AuditLog.objects.filter(
        action=AuditLog.Action.UPDATE,
        model_label="care.CarePlan",
        object_id=str(plan.pk),
    ).latest("created_at")
    assert log.actor == head_nurse_user

    client.post(reverse("care:plan_reopen", kwargs={"pk": plan.pk}))
    plan.refresh_from_db()
    assert plan.status == CarePlan.Status.ACTIVO
    assert plan.closure_reason == ""


def test_archived_resident_blocks_care_changes(
    client, head_nurse_user, caregiver_user, resident
):
    resident.is_active = False
    resident.save(update_fields=["is_active"])
    plan = make_plan(resident, head_nurse_user)
    record = make_record(resident, caregiver_user)
    client.force_login(head_nurse_user)

    plan_response = client.post(
        reverse("care:plan_create", kwargs={"resident_pk": resident.pk}),
        {
            "title": "Otro plan",
            "need": "Necesidad.",
            "objective": "Objetivo.",
            "actions": "Acciones.",
            "start_date": timezone.localdate().isoformat(),
        },
    )
    assert plan_response.status_code == 302
    assert CarePlan.objects.count() == 1

    review_response = client.post(
        reverse("care:record_review", kwargs={"pk": record.pk}), {}
    )
    assert review_response.status_code == 302
    record.refresh_from_db()
    assert record.reviewed_at is None


# --- Datos ficticios --------------------------------------------------------


def test_seed_demo_creates_care_data_idempotently(settings):
    settings.DEMO_MODE = True
    call_command("seed_demo", verbosity=0)
    first_plans = CarePlan.objects.count()
    first_records = DailyCareRecord.objects.count()
    assert first_plans > 0
    assert first_records > 0

    call_command("seed_demo", verbosity=0)
    assert CarePlan.objects.count() == first_plans
    assert DailyCareRecord.objects.count() == first_records
