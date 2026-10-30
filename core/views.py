from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.utils import timezone
from django.views.generic import TemplateView

from accounts.models import Role
from audit.models import AuditLog
from care.models import CarePlan, DailyCareRecord
from incidents.models import Incident
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
            logs = AuditLog.objects.select_related("actor")
            if (
                self.request.user.role == Role.ADMINISTRACION
                and not self.request.user.is_superuser
            ):
                logs = logs.exclude(model_label="incidents.Incident")
            context["recent_logs"] = logs.order_by("-created_at")[:6]

        today = timezone.localdate()
        current_records = DailyCareRecord.objects.filter(
            status=DailyCareRecord.Status.VIGENTE
        )
        context["care_today_count"] = current_records.filter(
            recorded_at__date=today
        ).count()
        context["care_pending_review"] = current_records.filter(
            requires_nursing_review=True, reviewed_at__isnull=True
        ).count()
        context["active_plan_count"] = CarePlan.objects.filter(
            status=CarePlan.Status.ACTIVO, resident__is_active=True
        ).count()
        context["open_incident_count"] = Incident.objects.filter(
            status=Incident.Status.OPEN
        ).count()

        context["today"] = today
        context["greeting_name"] = (
            self.request.user.get_short_name() or self.request.user.email
        )
        return context
