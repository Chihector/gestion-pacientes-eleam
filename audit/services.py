from __future__ import annotations

from django.contrib.auth import get_user_model

from .context import get_current_context
from .models import AuditLog


def _actor_data(actor) -> tuple[int | None, str]:
    if actor is None or not getattr(actor, "is_authenticated", False):
        return None, ""
    full_name = ""
    try:
        full_name = actor.get_full_name().strip()
    except AttributeError:
        pass
    label = f"{full_name} <{actor.email}>" if full_name else str(actor)
    return actor.pk, label[:254]


def log_action(
    *,
    action: str,
    actor=None,
    instance=None,
    model_label: str | None = None,
    object_id: str | None = None,
    object_repr: str | None = None,
    changes: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    """Crea un registro explícito (por ejemplo, para cambios de contraseña).

    El actor por defecto es el usuario de la petición actual.
    """

    context = get_current_context()
    if actor is None:
        actor = context.user
    actor_id, actor_repr = _actor_data(actor)

    if instance is not None:
        model_label = model_label or instance._meta.label
        object_id = object_id or str(instance.pk)
        object_repr = object_repr or str(instance)

    return AuditLog.objects.create(
        actor_id=actor_id,
        actor_repr=actor_repr,
        action=action,
        model_label=model_label or "",
        object_id=object_id or "",
        object_repr=(object_repr or "")[:200],
        changes=changes or {},
        ip_address=ip_address or context.ip_address,
    )
