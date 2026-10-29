from __future__ import annotations

import pytest
from django.urls import reverse

from accounts.models import Role, User, active_admin_count
from audit.models import AuditLog

pytestmark = pytest.mark.django_db


def test_login_uses_email(client, nurse_user):
    response = client.post(
        reverse("accounts:login"),
        {"username": nurse_user.email, "password": "ClaveSegura2026!"},
    )

    assert response.status_code == 302
    assert response["Location"] == reverse("core:dashboard")
    assert client.session["_auth_user_id"] == str(nurse_user.pk)


def test_login_rejects_wrong_password(client, nurse_user):
    response = client.post(
        reverse("accounts:login"),
        {"username": nurse_user.email, "password": "incorrecta"},
    )

    assert response.status_code == 200
    assert response.context["form"].non_field_errors()


def test_inactive_user_cannot_login(client, make_user):
    user = make_user("inactivo@example.test", Role.CUIDADOR, is_active=False)
    response = client.post(
        reverse("accounts:login"),
        {"username": user.email, "password": "ClaveSegura2026!"},
    )

    assert response.status_code == 200
    assert response.context["form"].non_field_errors()
    assert "_auth_user_id" not in client.session


def test_logout_requires_post(client, nurse_user):
    client.force_login(nurse_user)
    assert client.get(reverse("accounts:logout")).status_code == 405

    response = client.post(reverse("accounts:logout"))
    assert response.status_code == 302
    assert response["Location"] == reverse("accounts:login")


def test_only_administration_can_manage_users(client, admin_user, direction_user, nurse_user):
    client.force_login(admin_user)
    assert client.get(reverse("accounts:user_list")).status_code == 200

    client.force_login(direction_user)
    assert client.get(reverse("accounts:user_list")).status_code == 403

    client.force_login(nurse_user)
    assert client.get(reverse("accounts:user_list")).status_code == 403


def test_admin_cannot_deactivate_own_account(client, admin_user):
    client.force_login(admin_user)
    response = client.post(
        reverse("accounts:user_update", args=[admin_user.pk]),
        {
            "email": admin_user.email,
            "first_name": admin_user.first_name,
            "last_name": admin_user.last_name,
            "role": Role.ADMINISTRACION,
        },
    )

    assert response.status_code == 200
    assert "No puedes desactivar tu propia cuenta" in response.context["form"].errors["is_active"][0]
    admin_user.refresh_from_db()
    assert admin_user.is_active is True


def test_admin_can_deactivate_another_user_and_audit_is_written(
    client, admin_user, make_user
):
    target = make_user("tecnico2@example.test", Role.TECNICO)
    client.force_login(admin_user)

    response = client.post(
        reverse("accounts:user_update", args=[target.pk]),
        {
            "email": target.email,
            "first_name": target.first_name,
            "last_name": target.last_name,
            "role": Role.TECNICO,
        },
    )

    assert response.status_code == 302
    target.refresh_from_db()
    assert target.is_active is False
    log = AuditLog.objects.get(
        action=AuditLog.Action.DEACTIVATE,
        model_label="accounts.User",
        object_id=str(target.pk),
    )
    assert log.actor == admin_user


def test_active_admin_count_excludes_given_user(admin_user):
    assert active_admin_count() == 1
    assert active_admin_count(exclude_pk=admin_user.pk) == 0


def test_admin_can_create_user_with_known_password(client, admin_user):
    client.force_login(admin_user)
    response = client.post(
        reverse("accounts:user_create"),
        {
            "email": "Nueva.Persona@Example.Test",
            "first_name": "Nueva",
            "last_name": "Persona",
            "role": Role.TECNICO,
            "is_active": "on",
            "password1": "ClaveInicial2026!",
            "password2": "ClaveInicial2026!",
        },
    )

    assert response.status_code == 302
    created = User.objects.get(email="nueva.persona@example.test")
    assert created.check_password("ClaveInicial2026!")
    assert created.created_at is not None


def test_admin_password_reset_is_audited(client, admin_user, technician_user):
    client.force_login(admin_user)
    response = client.post(
        reverse("accounts:user_password_reset", args=[technician_user.pk]),
        {
            "new_password1": "Temporal2026!Segura",
            "new_password2": "Temporal2026!Segura",
        },
    )

    assert response.status_code == 302
    technician_user.refresh_from_db()
    assert technician_user.check_password("Temporal2026!Segura")
    log = AuditLog.objects.get(
        action=AuditLog.Action.PASSWORD_RESET,
        object_id=str(technician_user.pk),
    )
    assert log.actor == admin_user
    assert "password" not in log.changes


def test_password_change_is_audited_and_not_stored(client, nurse_user):
    client.force_login(nurse_user)
    response = client.post(
        reverse("accounts:password_change"),
        {
            "old_password": "ClaveSegura2026!",
            "new_password1": "OtraClave2026!",
            "new_password2": "OtraClave2026!",
        },
    )

    assert response.status_code == 302
    nurse_user.refresh_from_db()
    assert nurse_user.check_password("OtraClave2026!")
    log = AuditLog.objects.get(
        action=AuditLog.Action.PASSWORD,
        object_id=str(nurse_user.pk),
    )
    assert log.actor == nurse_user
    assert log.changes == {}
