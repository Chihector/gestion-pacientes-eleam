from __future__ import annotations

import contextvars
import ipaddress
from dataclasses import dataclass


@dataclass(frozen=True)
class AuditContext:
    user: object | None = None
    ip_address: str | None = None
    user_agent: str = ""


_current_context: contextvars.ContextVar[AuditContext] = contextvars.ContextVar(
    "audit_context", default=AuditContext()
)


def get_current_context() -> AuditContext:
    return _current_context.get()


def set_current_context(
    user=None, ip_address: str | None = None, user_agent: str = ""
):
    """Fija el contexto de la petición y devuelve el token para restaurarlo."""

    return _current_context.set(
        AuditContext(user=user, ip_address=ip_address, user_agent=user_agent[:300])
    )


def reset_current_context(token) -> None:
    _current_context.reset(token)


def normalize_ip(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return str(ipaddress.ip_address(value.strip()))
    except ValueError:
        return None
