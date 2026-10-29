from __future__ import annotations

from datetime import date

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse

from accounts.models import Role, User
from audit.models import AuditLog
from residents.models import Contact, Resident
from residents.rut import calculate_dv, clean_rut, rut_display, validate_rut

pytestmark = pytest.mark.django_db


# --- RUT y modelo -----------------------------------------------------------


def test_rut_helpers_normalize_format_and_validate():
    assert clean_rut("12.345.678-5") == "12345678-5"
    assert clean_rut(" 12345678 5 ") == "12345678-5"
    assert rut_display("12345678-5") == "12.345.678-5"
    assert rut_display("11222333-9") == "11.222.333-9"
    assert validate_rut("12.345.678-5") is True
    assert validate_rut("12.345.678-4") is False
    assert validate_rut("123") is False


def test_resident_properties(resident):
    assert resident.full_name == "Rosa Ficticia Pérez"
    assert resident.initials == "RF"
    assert resident.age >= 80
    assert resident.has_allergies is True
    assert resident.rut_formatted == "11.222.333-9"


def test_new_resident_defaults_to_active_and_not_demo(resident):
    otra = Resident.objects.create(
        first_name="Pedro",
        last_name="Muestra Díaz",
        rut=f"15678901-{calculate_dv('15678901')}",
        birth_date=date(1950, 2, 17),
        admission_date=date(2023, 2, 20),
    )
    assert otra.is_active is True
    assert otra.is_demo is False


# --- Permisos y creación ----------------------------------------------------


def test_anonymous_user_is_redirected_to_login(client):
    response = client.get(reverse("residents:list"))
    assert response.status_code == 302
    assert reverse("accounts:login") in response["Location"]


def test_nurse_can_create_resident_and_audit_is_written(client, nurse_user):
    client.force_login(nurse_user)
    response = client.post(
        reverse("residents:create"),
        {
            "first_name": "Nuevo",
            "last_name": "Residente Ficticio",
            "preferred_name": "",
            "rut": "12.345.678-5",
            "birth_date": "1940-01-01",
            "sex": Resident.Sex.MASCULINO,
            "room": "8",
            "admission_date": "2024-01-01",
            "status": Resident.Status.ACTIVO,
            "health_insurance": Resident.HealthInsurance.FONASA,
        },
    )

    assert response.status_code == 302
    created = Resident.objects.get(rut="12345678-5")
    assert created.created_by == nurse_user
    assert created.updated_by == nurse_user

    log = AuditLog.objects.get(
        action=AuditLog.Action.CREATE,
        model_label="residents.Resident",
        object_id=str(created.pk),
    )
    assert log.actor == nurse_user
    assert "first_name" in log.changes


def test_create_rejects_duplicate_rut(client, nurse_user, resident):
    client.force_login(nurse_user)
    response = client.post(
        reverse("residents:create"),
        {
            "first_name": "Otra",
            "last_name": "Persona",
            "rut": "11.222.333-9",
            "birth_date": "1940-01-01",
            "sex": Resident.Sex.FEMENINO,
            "admission_date": "2024-01-01",
            "status": Resident.Status.ACTIVO,
            "health_insurance": Resident.HealthInsurance.FONASA,
        },
    )

    assert response.status_code == 200
    assert "Ya existe una ficha con este RUT" in response.context["form"].errors["rut"][0]
    assert Resident.objects.count() == 1


def test_create_rejects_invalid_rut(client, nurse_user):
    client.force_login(nurse_user)
    response = client.post(
        reverse("residents:create"),
        {
            "first_name": "Persona",
            "last_name": "Inválida",
            "rut": "12.345.678-4",
            "birth_date": "1940-01-01",
            "sex": Resident.Sex.NO_INFORMA,
            "admission_date": "2024-01-01",
            "status": Resident.Status.ACTIVO,
            "health_insurance": Resident.HealthInsurance.NO_INFORMA,
        },
    )

    assert response.status_code == 200
    assert "RUT válido" in response.context["form"].errors["rut"][0]


@pytest.mark.parametrize("role", [Role.DIRECCION, Role.TECNICO, Role.CUIDADOR])
def test_roles_without_permission_cannot_create(client, make_user, role):
    user = make_user(f"{role.lower()}@example.test", role)
    client.force_login(user)
    response = client.get(reverse("residents:create"))
    assert response.status_code == 403


def test_only_nurse_can_edit_clinical_data(client, admin_user, nurse_user, resident):
    client.force_login(admin_user)
    assert client.get(reverse("residents:clinical_update", args=[resident.pk])).status_code == 403

    client.force_login(nurse_user)
    response = client.post(
        reverse("residents:clinical_update", args=[resident.pk]),
        {
            "allergies": "Penicilina, látex",
            "relevant_background": "Hipertensión arterial.",
            "clinical_notes": "Camina con apoyo.",
        },
    )
    assert response.status_code == 302
    resident.refresh_from_db()
    assert resident.allergies == "Penicilina, látex"


# --- Listado, búsqueda y archivado ------------------------------------------


def test_list_search_by_name_and_rut(client, nurse_user, resident):
    client.force_login(nurse_user)

    by_name = client.get(reverse("residents:list"), {"q": "Rosa"})
    assert [r.pk for r in by_name.context["residents"]] == [resident.pk]

    by_rut = client.get(reverse("residents:list"), {"q": "11.222.333-9"})
    assert [r.pk for r in by_rut.context["residents"]] == [resident.pk]

    sin_resultados = client.get(reverse("residents:list"), {"q": "No existe"})
    assert list(sin_resultados.context["residents"]) == []


def test_list_hides_archived_unless_requested(client, nurse_user, resident):
    resident.is_active = False
    resident.save(update_fields=["is_active", "updated_at"])
    client.force_login(nurse_user)

    response = client.get(reverse("residents:list"))
    assert list(response.context["residents"]) == []

    response = client.get(reverse("residents:list"), {"archivados": "1"})
    assert [r.pk for r in response.context["residents"]] == [resident.pk]


def test_list_uses_partial_for_htmx(client, nurse_user, resident):
    client.force_login(nurse_user)
    response = client.get(reverse("residents:list"), HTTP_HX_REQUEST="true")
    assert response.status_code == 200
    assert b"residentes-resultados" in response.content
    assert response.templates[0].name == "residents/_results.html"


def test_archive_and_restore_are_audited(client, nurse_user, resident):
    client.force_login(nurse_user)

    response = client.post(reverse("residents:archive", args=[resident.pk]))
    assert response.status_code == 302
    resident.refresh_from_db()
    assert resident.is_active is False
    assert AuditLog.objects.filter(
        action=AuditLog.Action.ARCHIVE,
        object_id=str(resident.pk),
        actor=nurse_user,
    ).exists()

    client.post(reverse("residents:archive", args=[resident.pk]))
    resident.refresh_from_db()
    assert resident.is_active is True
    assert AuditLog.objects.filter(
        action=AuditLog.Action.RESTORE,
        object_id=str(resident.pk),
        actor=nurse_user,
    ).exists()


def test_archived_resident_cannot_be_edited_until_restored(client, nurse_user, resident):
    resident.is_active = False
    resident.save(update_fields=["is_active", "updated_at"])
    client.force_login(nurse_user)

    response = client.get(reverse("residents:update", args=[resident.pk]))
    assert response.status_code == 302
    assert response["Location"] == reverse("residents:detail", args=[resident.pk])


# --- Contactos --------------------------------------------------------------


def test_only_one_primary_contact_per_resident(resident):
    first = Contact.objects.create(
        resident=resident,
        name="María Ficticia",
        relationship="Hija",
        phone="+56 9 0000 0001",
        is_primary=True,
    )
    second = Contact.objects.create(
        resident=resident,
        name="Jorge Ficticio",
        relationship="Hijo",
        phone="+56 9 0000 0002",
        is_primary=True,
    )

    first.refresh_from_db()
    assert first.is_primary is False
    assert second.is_primary is True
    assert Contact.objects.filter(resident=resident, is_primary=True).count() == 1


def test_contact_delete_is_audited(client, nurse_user, resident):
    contact = Contact.objects.create(
        resident=resident,
        name="María Ficticia",
        relationship="Hija",
        phone="+56 9 0000 0001",
        is_primary=True,
    )
    client.force_login(nurse_user)

    response = client.post(reverse("residents:contact_delete", args=[contact.pk]))
    assert response.status_code == 302
    assert Contact.objects.filter(pk=contact.pk).exists() is False

    log = AuditLog.objects.get(
        action=AuditLog.Action.DELETE,
        model_label="residents.Contact",
        object_id=str(contact.pk),
    )
    assert log.actor == nurse_user
    assert log.changes["name"]["before"] == "María Ficticia"


def test_contact_create_assigns_resident(client, nurse_user, resident):
    client.force_login(nurse_user)
    response = client.post(
        reverse("residents:contact_create", args=[resident.pk]),
        {
            "name": "Nuevo Contacto",
            "relationship": "Vecina",
            "phone": "+56 9 1111 2222",
            "email": "contacto@example.test",
            "is_primary": "on",
            "notes": "",
        },
    )
    assert response.status_code == 302
    contact = Contact.objects.get(name="Nuevo Contacto")
    assert contact.resident == resident
    assert contact.is_primary is True


# --- Seed de demostración ---------------------------------------------------


def test_seed_demo_is_idempotent_and_marks_demo_data(settings):
    settings.DEMO_MODE = True
    call_command("seed_demo", verbosity=0)
    call_command("seed_demo", verbosity=0)

    assert User.objects.count() == 5
    assert Resident.objects.count() == 9
    assert Resident.objects.filter(is_demo=True).count() == 9
    assert Contact.objects.count() == 9
    assert User.objects.get(email="enfermeria@example.test").check_password(
        "DemoEleam2026!"
    )


def test_seed_demo_refuses_non_demo_records(settings):
    settings.DEMO_MODE = True
    Resident.objects.create(
        first_name="Dato",
        last_name="Real",
        rut=f"15678901-{calculate_dv('15678901')}",
        birth_date=date(1950, 1, 1),
        admission_date=date(2023, 1, 1),
        is_demo=False,
    )

    with pytest.raises(CommandError):
        call_command("seed_demo", verbosity=0)


def test_seed_demo_refuses_when_demo_mode_is_off(settings):
    settings.DEMO_MODE = False

    with pytest.raises(CommandError):
        call_command("seed_demo", verbosity=0)
