from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.utils import timezone
from django.views.generic import TemplateView

from audit.models import AuditLog
from residents.models import Contact, Resident


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active = Resident.objects.filter(is_active=True)
        primary_contacts = Prefetch(
            "contacts",
            queryset=Contact.objects.filter(is_primary=True),
            to_attr="primary_contacts",
        )

        context["active_count"] = active.count()
        context["allergy_count"] = active.exclude(allergies="").count()
        context["hospitalized_count"] = active.filter(
            status=Resident.Status.HOSPITALIZADO
        ).count()
        context["archived_count"] = Resident.objects.filter(is_active=False).count()
        context["missing_contact_count"] = (
            active.exclude(contacts__is_primary=True).distinct().count()
        )

        context["recent_residents"] = (
            active.select_related("updated_by")
            .prefetch_related(primary_contacts)
            .order_by("-created_at")[:5]
        )
        context["allergy_alerts"] = (
            active.exclude(allergies="")
            .prefetch_related(primary_contacts)
            .order_by("last_name", "first_name")[:5]
        )
        context["missing_contact_residents"] = (
            active.exclude(contacts__is_primary=True)
            .distinct()
            .order_by("last_name", "first_name")[:3]
        )

        if self.request.user.can_view_audit:
            context["recent_logs"] = (
                AuditLog.objects.select_related("actor").order_by("-created_at")[:6]
            )

        context["today"] = timezone.localdate()
        context["greeting_name"] = (
            self.request.user.get_short_name() or self.request.user.email
        )
        return context
