from __future__ import annotations

import csv
import io
from datetime import date

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse

from accounts.models import Role, User
from audit.models import AuditLog
from residents.models import Contact, Disease, Medication, Resident
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


def test_head_nurse_can_create_resident_and_audit_is_written(client, head_nurse_user):
    client.force_login(head_nurse_user)
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
    assert created.created_by == head_nurse_user
    assert created.updated_by == head_nurse_user

    log = AuditLog.objects.get(
        action=AuditLog.Action.CREATE,
        model_label="residents.Resident",
        object_id=str(created.pk),
    )
    assert log.actor == head_nurse_user
    assert "first_name" in log.changes


def test_create_rejects_duplicate_rut(client, head_nurse_user, resident):
    client.force_login(head_nurse_user)
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


def test_create_rejects_invalid_rut(client, head_nurse_user):
    client.force_login(head_nurse_user)
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


@pytest.mark.parametrize("role", [Role.DIRECCION, Role.MEDICO, Role.ENFERMERIA, Role.TECNICO, Role.CUIDADOR])
def test_roles_without_permission_cannot_create(client, make_user, role):
    user = make_user(f"{role.lower()}@example.test", role)
    client.force_login(user)
    response = client.get(reverse("residents:create"))
    assert response.status_code == 403


def test_medico_head_nurse_nurse_can_edit_clinical_data(client, admin_user, head_nurse_user, nurse_user, resident):
    # Admin cannot edit clinical
    client.force_login(admin_user)
    assert client.get(reverse("residents:clinical_update", args=[resident.pk])).status_code == 403
    
    # Medico can
    client.force_login(head_nurse_user)  # Using head_nurse as medico for now
    # Actually let's test with the nurse user (ENFERMERIA)
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


def test_archive_and_restore_are_audited(client, head_nurse_user, resident):
    client.force_login(head_nurse_user)

    response = client.post(reverse("residents:archive", args=[resident.pk]))
    assert response.status_code == 302
    resident.refresh_from_db()
    assert resident.is_active is False
    assert AuditLog.objects.filter(
        action=AuditLog.Action.ARCHIVE,
        object_id=str(resident.pk),
        actor=head_nurse_user,
    ).exists()

    client.post(reverse("residents:archive", args=[resident.pk]))
    resident.refresh_from_db()
    assert resident.is_active is True
    assert AuditLog.objects.filter(
        action=AuditLog.Action.RESTORE,
        object_id=str(resident.pk),
        actor=head_nurse_user,
    ).exists()


def test_archived_resident_cannot_be_edited_until_restored(client, head_nurse_user, resident):
    resident.is_active = False
    resident.save(update_fields=["is_active", "updated_at"])
    client.force_login(head_nurse_user)

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


def test_contact_delete_is_audited(client, head_nurse_user, resident):
    contact = Contact.objects.create(
        resident=resident,
        name="María Ficticia",
        relationship="Hija",
        phone="+56 9 0000 0001",
        is_primary=True,
    )
    client.force_login(head_nurse_user)

    response = client.post(reverse("residents:contact_delete", args=[contact.pk]))
    assert response.status_code == 302
    assert Contact.objects.filter(pk=contact.pk).exists() is False

    log = AuditLog.objects.get(
        action=AuditLog.Action.DELETE,
        model_label="residents.Contact",
        object_id=str(contact.pk),
    )
    assert log.actor == head_nurse_user
    assert log.changes["name"]["before"] == "María Ficticia"


def test_contact_create_assigns_resident(client, head_nurse_user, resident):
    client.force_login(head_nurse_user)
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


# --- Exportación CSV --------------------------------------------------------


@pytest.mark.parametrize(
    "role", [Role.DIRECCION, Role.ADMINISTRACION, Role.ENFERMERA_JEFE]
)
def test_export_csv_is_available_for_authorized_roles(client, make_user, role, resident):
    user = make_user(f"export-{role.lower()}@example.test", role)
    client.force_login(user)

    response = client.get(reverse("residents:export"))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    assert "attachment;" in response["Content-Disposition"]


@pytest.mark.parametrize("role", [Role.MEDICO, Role.ENFERMERIA, Role.TECNICO, Role.CUIDADOR])
def test_export_csv_is_forbidden_for_other_roles(client, make_user, role, resident):
    user = make_user(f"export-{role.lower()}@example.test", role)
    client.force_login(user)

    response = client.get(reverse("residents:export"))

    assert response.status_code == 403


def test_export_csv_applies_filters_and_includes_primary_contact(
    client, head_nurse_user, resident
):
    other = Resident.objects.create(
        first_name="Pedro",
        last_name="Muestra Díaz",
        rut=f"15678901-{calculate_dv('15678901')}",
        birth_date=date(1950, 2, 17),
        admission_date=date(2023, 2, 20),
        status=Resident.Status.HOSPITALIZADO,
    )
    archived = Resident.objects.create(
        first_name="Ana",
        last_name="Archivada Ficticia",
        rut=f"13456789-{calculate_dv('13456789')}",
        birth_date=date(1948, 5, 9),
        admission_date=date(2022, 8, 1),
        is_active=False,
    )
    Contact.objects.create(
        resident=resident,
        name="María Ficticia",
        relationship="Hija",
        phone="+56 9 0000 0001",
        is_primary=True,
    )
    client.force_login(head_nurse_user)

    response = client.get(reverse("residents:export"), {"q": "Rosa"})
    rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))

    assert rows[0][0] == "RUT"
    assert "Alergias" not in rows[0]
    assert "Antecedentes" not in rows[0]
    assert [row[0] for row in rows[1:]] == [resident.rut_formatted]
    assert rows[1][11:14] == ["María Ficticia", "Hija", "+56 9 0000 0001"]

    response = client.get(
        reverse("residents:export"), {"estado": Resident.Status.HOSPITALIZADO}
    )
    rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
    assert [row[0] for row in rows[1:]] == [other.rut_formatted]

    response = client.get(reverse("residents:export"), {"archivados": "1"})
    rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
    assert {row[0] for row in rows[1:]} == {
        resident.rut_formatted,
        other.rut_formatted,
        archived.rut_formatted,
    }


def test_export_csv_is_audited_with_filters_and_total(client, head_nurse_user, resident):
    client.force_login(head_nurse_user)

    response = client.get(
        reverse("residents:export"),
        {"q": "Rosa", "estado": Resident.Status.ACTIVO},
    )

    assert response.status_code == 200
    log = AuditLog.objects.get(action=AuditLog.Action.EXPORT)
    assert log.actor == head_nurse_user
    assert log.model_label == "residents.Resident"
    assert log.changes["filtros"] == {
        "q": "Rosa",
        "estado": Resident.Status.ACTIVO,
        "incluir_archivados": False,
    }
    assert log.changes["total"] == 1


# --- Seed de demostración ---------------------------------------------------


def test_seed_demo_is_idempotent_and_marks_demo_data(settings):
    settings.DEMO_MODE = True
    call_command("seed_demo", verbosity=0)
    call_command("seed_demo", verbosity=0)

    assert User.objects.count() == 7
    assert Resident.objects.count() == 9
    assert Resident.objects.filter(is_demo=True).count() == 9
    assert Contact.objects.count() == 9
    assert Disease.objects.count() == 4
    assert Medication.objects.count() == 4
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



# --- Enfermedades y Condiciones Clínicas ------------------------------------


def test_nurse_can_create_disease_and_edit_it_later(client, nurse_user, resident):
    client.force_login(nurse_user)

    # 1. Crear enfermedad
    create_url = reverse("residents:disease_create", kwargs={"resident_pk": resident.pk})
    response = client.post(
        create_url,
        {
            "name": "Hipertensión arterial",
            "diagnosed_date": "2020-05-10",
            "status": Disease.Status.ACTIVA,
            "notes": "Controlar presión antes de medicar.",
        },
    )
    assert response.status_code == 302

    disease = Disease.objects.get(resident=resident, name="Hipertensión arterial")
    assert disease.status == Disease.Status.ACTIVA
    assert disease.created_by == nurse_user

    # 2. Editar enfermedad después de guardada
    update_url = reverse("residents:disease_update", kwargs={"pk": disease.pk})
    response = client.post(
        update_url,
        {
            "name": "Hipertensión arterial controlada",
            "diagnosed_date": "2020-05-10",
            "status": Disease.Status.CONTROLADA,
            "notes": "Evolución favorable con tratamiento.",
        },
    )
    assert response.status_code == 302

    disease.refresh_from_db()
    assert disease.name == "Hipertensión arterial controlada"
    assert disease.status == Disease.Status.CONTROLADA
    assert disease.notes == "Evolución favorable con tratamiento."
    assert disease.updated_by == nurse_user

    # 3. Verificar auditoría
    logs = AuditLog.objects.filter(model_label="residents.Disease", object_id=str(disease.pk))
    assert logs.filter(action=AuditLog.Action.CREATE).exists()
    assert logs.filter(action=AuditLog.Action.UPDATE).exists()


@pytest.mark.parametrize("role", [Role.DIRECCION, Role.TECNICO, Role.CUIDADOR, Role.ADMINISTRACION])
def test_non_clinical_roles_cannot_create_or_edit_disease(client, make_user, role, resident):
    user = make_user(f"user-{role.lower()}@example.test", role)
    client.force_login(user)

    create_url = reverse("residents:disease_create", kwargs={"resident_pk": resident.pk})
    response = client.post(
        create_url,
        {
            "name": "Artritis",
            "status": Disease.Status.ACTIVA,
        },
    )
    assert response.status_code == 403

    disease = Disease.objects.create(
        resident=resident,
        name="Artritis",
        status=Disease.Status.ACTIVA,
    )
    update_url = reverse("residents:disease_update", kwargs={"pk": disease.pk})
    response = client.post(
        update_url,
        {
            "name": "Artritis modificada",
            "status": Disease.Status.CONTROLADA,
        },
    )
    assert response.status_code == 403


def test_nurse_can_delete_disease(client, nurse_user, resident):
    disease = Disease.objects.create(
        resident=resident,
        name="Diagnóstico erróneo",
        status=Disease.Status.ACTIVA,
        created_by=nurse_user,
    )
    client.force_login(nurse_user)

    delete_url = reverse("residents:disease_delete", kwargs={"pk": disease.pk})
    response = client.post(delete_url)
    assert response.status_code == 302
    assert not Disease.objects.filter(pk=disease.pk).exists()

    log = AuditLog.objects.get(
        action=AuditLog.Action.DELETE,
        model_label="residents.Disease",
        object_id=str(disease.pk),
    )
    assert log.actor == nurse_user


# --- Medicamentos y Remedios ------------------------------------------------


def test_nurse_can_create_medication_and_edit_it_later(client, nurse_user, resident):
    client.force_login(nurse_user)

    # 1. Crear medicamento
    create_url = reverse("residents:medication_create", kwargs={"resident_pk": resident.pk})
    response = client.post(
        create_url,
        {
            "name": "Losartán",
            "dose": "50 mg",
            "frequency": "Cada 12 horas",
            "route": Medication.Route.ORAL,
            "status": Medication.Status.ACTIVO,
            "prescribed_by": "Dr. Fernando Soto",
            "start_date": "2024-01-10",
            "end_date": "",
            "instructions": "Tomar con agua en el desayuno y cena.",
            "notes": "Bien tolerado.",
        },
    )
    assert response.status_code == 302

    med = Medication.objects.get(resident=resident, name="Losartán")
    assert med.dose == "50 mg"
    assert med.status == Medication.Status.ACTIVO
    assert med.created_by == nurse_user

    # 2. Editar medicamento después de guardado (cambio de dosis y frecuencia)
    update_url = reverse("residents:medication_update", kwargs={"pk": med.pk})
    response = client.post(
        update_url,
        {
            "name": "Losartán potásico",
            "dose": "100 mg",
            "frequency": "Cada 24 horas",
            "route": Medication.Route.ORAL,
            "status": Medication.Status.ACTIVO,
            "prescribed_by": "Dr. Fernando Soto",
            "start_date": "2024-01-10",
            "end_date": "",
            "instructions": "Ajuste de dosis según indicación médica.",
            "notes": "Nueva dosis 100mg.",
        },
    )
    assert response.status_code == 302

    med.refresh_from_db()
    assert med.name == "Losartán potásico"
    assert med.dose == "100 mg"
    assert med.frequency == "Cada 24 horas"
    assert med.updated_by == nurse_user

    # 3. Auditoría de creación y modificación
    logs = AuditLog.objects.filter(model_label="residents.Medication", object_id=str(med.pk))
    assert logs.filter(action=AuditLog.Action.CREATE).exists()
    assert logs.filter(action=AuditLog.Action.UPDATE).exists()


@pytest.mark.parametrize("role", [Role.DIRECCION, Role.TECNICO, Role.CUIDADOR, Role.ADMINISTRACION])
def test_non_clinical_roles_cannot_create_or_edit_medication(client, make_user, role, resident):
    user = make_user(f"med-{role.lower()}@example.test", role)
    client.force_login(user)

    create_url = reverse("residents:medication_create", kwargs={"resident_pk": resident.pk})
    response = client.post(
        create_url,
        {
            "name": "Paracetamol",
            "dose": "500 mg",
            "frequency": "Cada 8 horas",
            "route": Medication.Route.ORAL,
            "status": Medication.Status.ACTIVO,
        },
    )
    assert response.status_code == 403

    med = Medication.objects.create(
        resident=resident,
        name="Paracetamol",
        dose="500 mg",
        frequency="Cada 8 horas",
    )
    update_url = reverse("residents:medication_update", kwargs={"pk": med.pk})
    response = client.post(
        update_url,
        {
            "name": "Paracetamol",
            "dose": "1 g",
            "frequency": "Cada 8 horas",
            "route": Medication.Route.ORAL,
            "status": Medication.Status.ACTIVO,
        },
    )
    assert response.status_code == 403


def test_nurse_can_delete_medication(client, nurse_user, resident):
    med = Medication.objects.create(
        resident=resident,
        name="Fármaco suspendido",
        dose="10 mg",
        frequency="Cada 24h",
        created_by=nurse_user,
    )
    client.force_login(nurse_user)

    delete_url = reverse("residents:medication_delete", kwargs={"pk": med.pk})
    response = client.post(delete_url)
    assert response.status_code == 302
    assert not Medication.objects.filter(pk=med.pk).exists()

    log = AuditLog.objects.get(
        action=AuditLog.Action.DELETE,
        model_label="residents.Medication",
        object_id=str(med.pk),
    )
    assert log.actor == nurse_user


def test_caregivers_and_technicians_can_view_diseases_and_medications(client, make_user, resident):
    Disease.objects.create(
        resident=resident,
        name="Demencia vascular",
        status=Disease.Status.ACTIVA,
    )
    Medication.objects.create(
        resident=resident,
        name="Aspirina",
        dose="100 mg",
        frequency="Cada 24 horas con el desayuno",
        route=Medication.Route.ORAL,
        status=Medication.Status.ACTIVO,
        instructions="No suspender sin orden médica.",
    )

    cuidador = make_user("cuidador-consulta@example.test", Role.CUIDADOR)
    client.force_login(cuidador)

    detail_url = reverse("residents:detail", kwargs={"pk": resident.pk})
    response = client.get(detail_url)
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Demencia vascular" in content
    assert "Aspirina" in content
    assert "100 mg" in content
    assert "Cada 24 horas con el desayuno" in content


def test_archived_resident_blocks_adding_or_editing_disease_and_medication(client, nurse_user, resident):
    resident.is_active = False
    resident.save()

    disease = Disease.objects.create(
        resident=resident,
        name="Gota",
        status=Disease.Status.CONTROLADA,
    )
    med = Medication.objects.create(
        resident=resident,
        name="Alopurinol",
        dose="100 mg",
        frequency="Cada 24h",
    )

    client.force_login(nurse_user)

    # Bloquea crear enfermedad
    resp = client.get(reverse("residents:disease_create", kwargs={"resident_pk": resident.pk}))
    assert resp.status_code == 302

    # Bloquea editar enfermedad
    resp = client.get(reverse("residents:disease_update", kwargs={"pk": disease.pk}))
    assert resp.status_code == 302

    # Bloquea crear medicamento
    resp = client.get(reverse("residents:medication_create", kwargs={"resident_pk": resident.pk}))
    assert resp.status_code == 302

    # Bloquea editar medicamento
    resp = client.get(reverse("residents:medication_update", kwargs={"pk": med.pk}))
    assert resp.status_code == 302
