from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin):
    """Exige sesión y uno de los roles indicados.

    Los superusuarios técnicos pasan el control. La comprobación se hace en el
    servidor: ocultar un botón no es suficiente.
    """

    allowed_roles: tuple[str, ...] = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser and request.user.role not in self.allowed_roles:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
