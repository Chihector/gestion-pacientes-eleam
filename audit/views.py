from django.db.models import Q
from django.views.generic import ListView

from accounts.models import Role
from core.mixins import RoleRequiredMixin

from .models import AuditLog


class AuditListView(RoleRequiredMixin, ListView):
    allowed_roles = (Role.DIRECCION, Role.ADMINISTRACION)
    model = AuditLog
    template_name = "audit/audit_list.html"
    context_object_name = "logs"
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset().select_related("actor")
        if self.request.user.role == Role.ADMINISTRACION and not self.request.user.is_superuser:
            queryset = queryset.exclude(model_label="incidents.Incident")
        query = self.request.GET.get("q", "").strip()
        action = self.request.GET.get("accion", "").strip()
        model_label = self.request.GET.get("modelo", "").strip()

        if query:
            queryset = queryset.filter(
                Q(object_repr__icontains=query)
                | Q(actor_repr__icontains=query)
                | Q(actor__email__icontains=query)
                | Q(model_label__icontains=query)
            )
        if action:
            queryset = queryset.filter(action=action)
        if model_label:
            queryset = queryset.filter(model_label=model_label)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["actions"] = AuditLog.Action.choices
        model_labels = AuditLog.objects.all()
        if self.request.user.role == Role.ADMINISTRACION and not self.request.user.is_superuser:
            model_labels = model_labels.exclude(model_label="incidents.Incident")
        context["model_labels"] = model_labels.values_list(
            "model_label", flat=True
        ).distinct().order_by("model_label")
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "accion": self.request.GET.get("accion", ""),
            "modelo": self.request.GET.get("modelo", ""),
        }
        return context
