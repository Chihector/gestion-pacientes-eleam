from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .context import get_current_context
from .models import AuditLog, AuditedModel

_EXCLUDED_FIELDS = {
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
    "password",
    "last_login",
}


def _is_audited(sender) -> bool:
    try:
        return issubclass(sender, AuditedModel) or sender is get_user_model()
    except TypeError:
        return False


def _snapshot(instance) -> dict[str, dict]:
    data: dict[str, dict] = {}
    for field in instance._meta.concrete_fields:
        if field.name in _EXCLUDED_FIELDS:
            continue
        value = field.value_from_object(instance)
        data[field.name] = {
            "label": str(field.verbose_name),
            "value": value,
        }
    return data


def _actor() -> object | None:
    user = get_current_context().user
    if user is None or not getattr(user, "is_authenticated", False):
        return None
    return user


@receiver(pre_save, dispatch_uid="audit_capture_before_save")
def capture_before_save(sender, instance, **kwargs):
    if not _is_audited(sender):
        return

    user = _actor()
    if user is not None:
        if hasattr(instance, "created_by_id") and instance._state.adding and not instance.created_by_id:
            instance.created_by_id = user.pk
        if hasattr(instance, "updated_by_id"):
            instance.updated_by_id = user.pk

    if not instance._state.adding and instance.pk:
        previous = sender.objects.filter(pk=instance.pk).first()
        if previous is not None:
            instance._audit_before = _snapshot(previous)


@receiver(post_save, dispatch_uid="audit_write_after_save")
def write_after_save(sender, instance, created, **kwargs):
    if not _is_audited(sender):
        return

    after = _snapshot(instance)
    before = getattr(instance, "_audit_before", {})

    changes: dict[str, dict] = {}
    if created:
        for name, item in after.items():
            if item["value"] not in (None, "", [], {}):
                changes[name] = {
                    "label": item["label"],
                    "before": None,
                    "after": item["value"],
                }
    else:
        for name, item in after.items():
            old_value = before.get(name, {}).get("value")
            if old_value != item["value"]:
                changes[name] = {
                    "label": item["label"],
                    "before": old_value,
                    "after": item["value"],
                }

    action = getattr(instance, "_audit_action", None)
    if hasattr(instance, "_audit_action"):
        delattr(instance, "_audit_action")

    if not action:
        if created:
            action = AuditLog.Action.CREATE
        elif sender is get_user_model() and "is_active" in changes:
            action = (
                AuditLog.Action.DEACTIVATE
                if changes["is_active"]["after"] is False
                else AuditLog.Action.REACTIVATE
            )
        else:
            action = AuditLog.Action.UPDATE

    if action == AuditLog.Action.UPDATE and not changes:
        return

    context = get_current_context()
    user = _actor()
    actor_repr = ""
    if user is not None:
        full_name = user.get_full_name().strip()
        actor_repr = f"{full_name} <{user.email}>" if full_name else str(user)

    AuditLog.objects.create(
        actor_id=user.pk if user is not None else None,
        actor_repr=actor_repr[:254],
        action=action,
        model_label=sender._meta.label,
        object_id=str(instance.pk),
        object_repr=str(instance)[:200],
        changes=changes,
        ip_address=context.ip_address,
    )


@receiver(post_delete, dispatch_uid="audit_write_after_delete")
def write_after_delete(sender, instance, **kwargs):
    if not _is_audited(sender):
        return

    before = _snapshot(instance)
    changes = {
        name: {
            "label": item["label"],
            "before": item["value"],
            "after": None,
        }
        for name, item in before.items()
        if item["value"] not in (None, "", [], {})
    }

    context = get_current_context()
    user = _actor()
    actor_repr = ""
    if user is not None:
        full_name = user.get_full_name().strip()
        actor_repr = f"{full_name} <{user.email}>" if full_name else str(user)

    AuditLog.objects.create(
        actor_id=user.pk if user is not None else None,
        actor_repr=actor_repr[:254],
        action=AuditLog.Action.DELETE,
        model_label=sender._meta.label,
        object_id=str(instance.pk),
        object_repr=str(instance)[:200],
        changes=changes,
        ip_address=context.ip_address,
    )
