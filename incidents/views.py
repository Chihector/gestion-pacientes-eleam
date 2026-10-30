import csv
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from accounts.models import Role
from audit.models import AuditLog
from audit.services import log_action
from core.mixins import RoleRequiredMixin

from .forms import (
    IncidentCloseForm,
    IncidentFilterForm,
    IncidentForm,
    IncidentReportForm,
)
from .models import Incident

INCIDENT_VIEW_ROLES = (
    Role.DIRECCION,
    Role.ENFERMERIA,
    Role.TECNICO,
    Role.CUIDADOR,
)
INCIDENT_REPORT_ROLES = (Role.ENFERMERIA, Role.DIRECCION)
INCIDENT_CREATE_ROLES = (Role.ENFERMERIA, Role.TECNICO, Role.CUIDADOR)


class IncidentListView(RoleRequiredMixin, ListView):
    allowed_roles = INCIDENT_VIEW_ROLES
    model = Incident
    template_name = "incidents/incident_list.html"
    context_object_name = "incidents"
    paginate_by = 20

    def get_queryset(self):
        self.filter_form = IncidentFilterForm(self.request.GET)
        queryset = Incident.objects.select_related("resident", "created_by")
        if not self.filter_form.is_valid():
            return queryset.none()
        filters = self.filter_form.cleaned_data
        if filters["desde"]:
            queryset = queryset.filter(occurred_at__date__gte=filters["desde"])
        if filters["hasta"]:
            queryset = queryset.filter(occurred_at__date__lte=filters["hasta"])
        if filters["tipo"]:
            queryset = queryset.filter(incident_type=filters["tipo"])
        if filters["estado"]:
            queryset = queryset.filter(status=filters["estado"])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        context["can_report"] = (
            self.request.user.role in INCIDENT_CREATE_ROLES
            or self.request.user.is_superuser
        )
        context["can_view_reports"] = (
            self.request.user.role in INCIDENT_REPORT_ROLES
            or self.request.user.is_superuser
        )
        return context


class IncidentCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = INCIDENT_CREATE_ROLES
    model = Incident
    form_class = IncidentForm
    template_name = "incidents/incident_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Reportar un incidente"
        context["submit_label"] = "Enviar reporte"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Incidente reportado. Avisa a Enfermería de inmediato según el protocolo del ELEAM.",
        )
        return response


class IncidentDetailView(RoleRequiredMixin, DetailView):
    allowed_roles = INCIDENT_VIEW_ROLES
    model = Incident
    template_name = "incidents/incident_detail.html"
    context_object_name = "incident"

    def get_queryset(self):
        return Incident.objects.select_related(
            "resident", "created_by", "closed_by"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["close_form"] = IncidentCloseForm()
        context["can_close"] = (
            self.object.is_open
            and (
                self.request.user.is_superuser
                or self.request.user.role in INCIDENT_REPORT_ROLES
            )
        )
        return context


class IncidentCloseView(RoleRequiredMixin, View):
    allowed_roles = INCIDENT_REPORT_ROLES

    def post(self, request, pk, *args, **kwargs):
        incident = get_object_or_404(Incident, pk=pk)
        if incident.status != Incident.Status.OPEN:
            messages.info(request, "El incidente ya está cerrado.")
            return redirect(incident)

        form = IncidentCloseForm(request.POST)
        if not form.is_valid():
            messages.error(
                request,
                "El motivo de cierre debe tener entre 10 y 1000 caracteres.",
            )
            return redirect(incident)

        incident.status = Incident.Status.CLOSED
        incident.close_reason = form.cleaned_data["close_reason"]
        incident.closed_by = request.user
        incident.closed_at = timezone.now()
        incident._audit_action = AuditLog.Action.CLOSE
        incident.save(
            update_fields=[
                "status",
                "close_reason",
                "closed_by",
                "closed_at",
                "updated_by",
                "updated_at",
            ]
        )
        messages.success(request, "Incidente cerrado; el historial queda conservado.")
        return redirect(incident)


class IncidentReportView(RoleRequiredMixin, TemplateView):
    allowed_roles = INCIDENT_REPORT_ROLES
    template_name = "incidents/incident_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        initial = {
            "desde": today - timedelta(days=29),
            "hasta": today,
        }
        form_data = (
            self.request.GET
            if self.request.GET
            else {
                "desde": initial["desde"].isoformat(),
                "hasta": initial["hasta"].isoformat(),
            }
        )
        form = IncidentReportForm(form_data)
        context["report_form"] = form
        context["report_ready"] = form.is_valid()
        if not form.is_valid():
            return context

        start = form.cleaned_data["desde"]
        end = form.cleaned_data["hasta"]
        queryset = Incident.objects.filter(occurred_at__date__range=(start, end))
        context["report_start"] = start
        context["report_end"] = end
        context["total_count"] = queryset.count()
        context["open_count"] = queryset.filter(
            status=Incident.Status.OPEN
        ).count()
        context["closed_count"] = queryset.filter(
            status=Incident.Status.CLOSED
        ).count()
        context["by_type"] = self._choice_counts(
            queryset, "incident_type", Incident.Type.choices
        )
        context["by_severity"] = self._choice_counts(
            queryset, "severity", Incident.Severity.choices
        )
        return context

    @staticmethod
    def _choice_counts(queryset, field, choices):
        totals = {
            row[field]: row["total"]
            for row in queryset.values(field).annotate(total=Count("pk"))
        }
        return [
            {"label": label, "count": totals.get(value, 0)}
            for value, label in choices
        ]


class IncidentExportView(RoleRequiredMixin, View):
    allowed_roles = INCIDENT_REPORT_ROLES

    def get(self, request, *args, **kwargs):
        queryset = Incident.objects.select_related("resident", "created_by", "closed_by")
        form = IncidentFilterForm(request.GET)
        filters = {}
        if form.is_valid():
            filters = form.cleaned_data
            if filters.get("desde"):
                queryset = queryset.filter(occurred_at__date__gte=filters["desde"])
            if filters.get("hasta"):
                queryset = queryset.filter(occurred_at__date__lte=filters["hasta"])
            if filters.get("tipo"):
                queryset = queryset.filter(incident_type=filters["tipo"])
            if filters.get("estado"):
                queryset = queryset.filter(status=filters["estado"])

        incidents_list = list(queryset.order_by("-occurred_at", "-pk"))

        log_action(
            action=AuditLog.Action.EXPORT,
            actor=request.user,
            model_label="incidents.Incident",
            object_repr=f"Reporte de incidentes ({len(incidents_list)} registros)",
            changes={
                "filtros": {
                    "desde": str(request.GET.get("desde", "")),
                    "hasta": str(request.GET.get("hasta", "")),
                    "tipo": request.GET.get("tipo", ""),
                    "estado": request.GET.get("estado", ""),
                },
                "total": len(incidents_list),
            },
        )

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        filename = f"reporte_incidentes_{timezone.now():%Y%m%d_%H%M}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write("\ufeff")

        writer = csv.writer(response)
        writer.writerow([
            "ID",
            "Fecha y hora ocurrencia",
            "RUT Residente",
            "Residente",
            "Tipo de incidente",
            "Gravedad percibida",
            "Lugar",
            "Descripción de los hechos",
            "Acciones inmediatas",
            "Personas presentes",
            "Notificaciones realizadas",
            "Estado",
            "Reportado por",
            "Fecha reporte",
            "Fecha cierre",
            "Cerrado por",
            "Motivo / Seguimiento de cierre",
        ])

        for inc in incidents_list:
            writer.writerow([
                inc.pk,
                inc.occurred_at.strftime("%d/%m/%Y %H:%M") if inc.occurred_at else "",
                inc.resident.rut_formatted,
                inc.resident.get_full_name(),
                inc.get_incident_type_display(),
                inc.get_severity_display(),
                inc.location or "",
                inc.description,
                inc.immediate_actions,
                inc.witnesses or "",
                inc.notified or "",
                inc.get_status_display(),
                inc.created_by.get_full_name() if inc.created_by else "",
                inc.created_at.strftime("%d/%m/%Y %H:%M") if inc.created_at else "",
                inc.closed_at.strftime("%d/%m/%Y %H:%M") if inc.closed_at else "",
                inc.closed_by.get_full_name() if inc.closed_by else "",
                inc.close_reason or "",
            ])

        return response
