from __future__ import annotations

from .context import normalize_ip, reset_current_context, set_current_context


class AuditContextMiddleware:
    """Deja disponibles el usuario, la IP y el user-agent para la auditoría."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else None
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        raw_ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")
        token = set_current_context(
            user=user,
            ip_address=normalize_ip(raw_ip),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        try:
            return self.get_response(request)
        finally:
            reset_current_context(token)
