from __future__ import annotations

import csv
from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)

from accounts.models import Role
from audit.models import AuditLog
from audit.services import log_action
from core.mixins import RoleRequiredMixin
from residents.models import Resident

from .forms import CarePlanForm, DailyCareCorrectionForm, DailyCareRecordForm
from .models import CarePlan, DailyCareRecord


class ActiveResidentCareMixin:
    """Bloquea cambios sobre residentes archivados."""

    def resident_is_active(self, resident) -> bool:
        if resident.is_active:
            return True
        messages.warning(
            self.request,
            "La ficha está archivada. Reactívala antes de modificar sus cuidados.",
        )
        return False


# --- Planes de cuidados -----------------------------------------------------


class CarePlanCreateView(RoleRequiredMixin, ActiveResidentCareMixin, CreateView):
    allowed_roles = (Role.ENFERMERIA,)
    model = CarePlan
    form_class = CarePlanForm
    template_name = "care/plan_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.resident = get_object_or_404(Resident, pk=kwargs["resident_pk"])
        if not self.resident.is_active:
            messages.warning(
                request,
                "La ficha está archivada. Reactívala antes de crear un plan de cuidados.",
            )
            return redirect("residents:detail", pk=self.resident.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["resident"] = self.resident
        context["title"] = "Nuevo plan de cuidados"
        context["subtitle"] = (
            "Acuerda con el equipo el objetivo y las acciones concretas. "
            "El sistema no genera recomendaciones ni órdenes clínicas."
        )
        context["submit_label"] = "Crear plan"
        return context

    def form_valid(self, form):
        form.instance.resident = self.resident
        response = super().form_valid(form)
        messages.success(self.request, "Plan de cuidados creado.")
        return response

    def get_success_url(self):
        return (
            reverse("residents:detail", kwargs={"pk": self.resident.pk})
            + "#cuidados"
        )


class CarePlanUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = (Role.ENFERMERIA,)
    model = CarePlan
    form_class = CarePlanForm
    template_name = "care/plan_form.html"
    context_object_name = "plan"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.object = self.get_object()
        if not self.object.resident.is_active:
            messages.warning(
                request,
                "La ficha está archivada. Reactívala antes de modificar el plan.",
            )
            return redirect("residents:detail", pk=self.object.resident_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["resident"] = self.object.resident
        context["title"] = "Editar plan de cuidados"
        context["subtitle"] = (
            "Actualiza el plan según lo acordado con el equipo. "
            "Los cambios quedan registrados en la auditoría."
        )
        context["submit_label"] = "Guardar cambios"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Plan de cuidados actualizado.")
        return response

    def get_success_url(self):
        return (
            reverse("residents:detail", kwargs={"pk": self.object.resident_id})
            + "#cuidados"
        )


class CarePlanCloseView(RoleRequiredMixin, View):
    allowed_roles = (Role.ENFERMERIA,)

    def post(self, request, pk, *args, **kwargs):
        plan = get_object_or_404(CarePlan.objects.select_related("resident"), pk=pk)
        if not plan.resident.is_active:
            messages.warning(
                request,
                "La ficha está archivada. Reactívala antes de cerrar el plan.",
            )
            return redirect("residents:detail", pk=plan.resident_id)

        reason = (request.POST.get("closure_reason") or "").strip()
        if len(reason) < 10:
            messages.error(
                request,
                "Explica el motivo del cierre con al menos 10 caracteres.",
            )
            return redirect(
                reverse("residents:detail", kwargs={"pk": plan.resident_id})
                + "#cuidados"
            )

        plan.status = CarePlan.Status.CERRADO
        plan.closure_reason = reason[:500]
        plan.save(update_fields=["status", "closure_reason", "updated_by", "updated_at"])
        messages.success(request, "Plan de cuidados cerrado. El historial se conserva.")
        return redirect(
            reverse("residents:detail", kwargs={"pk": plan.resident_id})
            + "#cuidados"
        )


class CarePlanReopenView(RoleRequiredMixin, View):
    allowed_roles = (Role.ENFERMERIA,)

    def post(self, request, pk, *args, **kwargs):
        plan = get_object_or_404(CarePlan.objects.select_related("resident"), pk=pk)
        if not plan.resident.is_active:
            messages.warning(
                request,
                "La ficha está archivada. Reactívala antes de reactivar el plan.",
            )
            return redirect("residents:detail", pk=plan.resident_id)

        if plan.status != CarePlan.Status.CERRADO:
            messages.info(request, "El plan ya está activo.")
        else:
            plan.status = CarePlan.Status.ACTIVO
            plan.closure_reason = ""
            plan.save(
                update_fields=["status", "closure_reason", "updated_by", "updated_at"]
            )
            messages.success(request, "Plan de cuidados reactivado.")
        return redirect(
            reverse("residents:detail", kwargs={"pk": plan.resident_id})
            + "#cuidados"
        )


# --- Registros diarios ------------------------------------------------------


class DailyCareRecordListView(LoginRequiredMixin, ListView):
    model = DailyCareRecord
    template_name = "care/record_list.html"
    context_object_name = "records"
    paginate_by = 20

    def get_queryset(self):
        queryset = DailyCareRecord.objects.select_related(
            "resident", "care_plan", "created_by", "reviewed_by"
        )

        fecha = self.request.GET.get("fecha", "").strip()
        self.show_all_dates = fecha == "todas" or self.request.GET.get(
            "todas"
        ) in {"1", "true", "on"}
        self.target_date = None
        if not self.show_all_dates:
            try:
                self.target_date = date.fromisoformat(fecha) if fecha else timezone.localdate()
            except ValueError:
                self.target_date = timezone.localdate()
            queryset = queryset.filter(recorded_at__date=self.target_date)

        self.shift = self.request.GET.get("turno", "").strip()
        if self.shift in DailyCareRecord.Shift.values:
            queryset = queryset.filter(shift=self.shift)

        self.category = self.request.GET.get("categoria", "").strip()
        if self.category in DailyCareRecord.Category.values:
            queryset = queryset.filter(category=self.category)

        self.resident_id = self.request.GET.get("residente", "").strip()
        if self.resident_id.isdigit():
            queryset = queryset.filter(resident_id=self.resident_id)

        self.query = self.request.GET.get("q", "").strip()
        if self.query:
            compact = self.query.replace(".", "").replace(" ", "")
            queryset = queryset.filter(
                Q(resident__first_name__icontains=self.query)
                | Q(resident__last_name__icontains=self.query)
                | Q(resident__preferred_name__icontains=self.query)
                | Q(resident__rut__icontains=compact)
                | Q(description__icontains=self.query)
            )

        self.only_pending = self.request.GET.get("pendientes") in {"1", "true", "on"}
        if self.only_pending:
            queryset = queryset.filter(
                requires_nursing_review=True, reviewed_at__isnull=True
            )

        self.include_corrected = self.request.GET.get("corregidos") in {
            "1",
            "true",
            "on",
        }
        if not self.include_corrected:
            queryset = queryset.filter(status=DailyCareRecord.Status.VIGENTE)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current = DailyCareRecord.objects.filter(
            status=DailyCareRecord.Status.VIGENTE
        )
        today = timezone.localdate()
        context["today"] = today
        context["target_date"] = self.target_date
        context["fecha_value"] = (
            self.target_date.isoformat() if self.target_date else ""
        )
        context["show_all_dates"] = self.show_all_dates
        context["shift"] = self.shift
        context["category"] = self.category
        context["resident_filter"] = self.resident_id
        context["q"] = self.query
        context["only_pending"] = self.only_pending
        context["include_corrected"] = self.include_corrected
        context["shift_choices"] = DailyCareRecord.Shift.choices
        context["category_choices"] = DailyCareRecord.Category.choices
        context["today_count"] = current.filter(recorded_at__date=today).count()
        context["pending_count"] = current.filter(
            requires_nursing_review=True, reviewed_at__isnull=True
        ).count()
        context["corrected_today_count"] = DailyCareRecord.objects.filter(
            status=DailyCareRecord.Status.CORREGIDO, recorded_at__date=today
        ).count()
        context["active_plan_count"] = CarePlan.objects.filter(
            status=CarePlan.Status.ACTIVO, resident__is_active=True
        ).count()
        context["can_record"] = self.request.user.can_record_care
        context["can_export"] = self.request.user.can_export_care

        user = self.request.user
        for record in context["records"]:
            record.can_correct = record.can_be_corrected_by(user)
            record.can_review = record.can_be_reviewed_by(user)
        return context


class DailyCareRecordCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = (Role.ENFERMERIA, Role.TECNICO, Role.CUIDADOR)
    model = DailyCareRecord
    form_class = DailyCareRecordForm
    template_name = "care/record_form.html"

    def get_initial(self):
        initial = super().get_initial()
        resident_id = self.request.GET.get("residente", "").strip()
        if resident_id.isdigit():
            resident = Resident.objects.filter(
                pk=resident_id, is_active=True
            ).first()
            if resident:
                initial["resident"] = resident
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Registrar cuidado"
        context["subtitle"] = (
            "Registra lo realizado durante el turno. Describe hechos concretos, "
            "sin diagnósticos ni indicaciones de tratamiento."
        )
        context["submit_label"] = "Guardar registro"
        context["allow_save_and_new"] = True
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Cuidado registrado. Quedó asociado a tu nombre en la auditoría.",
        )
        return response

    def get_success_url(self):
        if "save_and_new" in self.request.POST:
            return (
                reverse("care:record_create")
                + f"?residente={self.object.resident_id}"
            )
        return reverse("care:record_detail", kwargs={"pk": self.object.pk})


class DailyCareRecordDetailView(LoginRequiredMixin, DetailView):
    model = DailyCareRecord
    template_name = "care/record_detail.html"
    context_object_name = "record"

    def get_queryset(self):
        return DailyCareRecord.objects.select_related(
            "resident",
            "care_plan",
            "created_by",
            "updated_by",
            "reviewed_by",
            "supersedes",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        record = self.object
        user = self.request.user
        context["can_correct"] = record.can_be_corrected_by(user)
        context["can_review"] = record.can_be_reviewed_by(user)
        context["correction"] = record.correction_record
        context["original"] = record.supersedes
        return context


class DailyCareRecordCorrectView(RoleRequiredMixin, FormView):
    allowed_roles = (Role.ENFERMERIA, Role.TECNICO, Role.CUIDADOR)
    form_class = DailyCareCorrectionForm
    template_name = "care/record_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.original = get_object_or_404(
            DailyCareRecord.objects.select_related("resident", "care_plan"),
            pk=kwargs["pk"],
        )
        if not self.original.is_owned_or_nurse(request.user):
            raise PermissionDenied
        if not self.original.resident.is_active:
            messages.warning(
                request,
                "La ficha está archivada. Reactívala antes de corregir el registro.",
            )
            return redirect("care:record_detail", pk=self.original.pk)
        if self.original.status != DailyCareRecord.Status.VIGENTE:
            messages.warning(
                request,
                "Este registro ya fue corregido. Abre la versión vigente para modificarlo.",
            )
            return redirect("care:record_detail", pk=self.original.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["original"] = self.original
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            {
                "recorded_at": timezone.localtime(self.original.recorded_at),
                "shift": self.original.shift,
                "category": self.original.category,
                "description": self.original.description,
                "observations": self.original.observations,
                "requires_nursing_review": self.original.requires_nursing_review,
            }
        )
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["original"] = self.original
        context["is_correction"] = True
        context["title"] = "Corregir registro de cuidado"
        context["subtitle"] = (
            "La corrección crea una nueva versión. El registro original no se "
            "borra y seguirá visible en el historial."
        )
        context["submit_label"] = "Guardar corrección"
        return context

    def form_valid(self, form):
        with transaction.atomic():
            new_record = form.save(commit=False)
            new_record.resident = self.original.resident
            new_record.care_plan = self.original.care_plan
            new_record.supersedes = self.original
            new_record.save()

            self.original.status = DailyCareRecord.Status.CORREGIDO
            self.original._audit_action = AuditLog.Action.CORRECTION
            self.original.save(
                update_fields=["status", "updated_by", "updated_at"]
            )

        self.object = new_record
        messages.success(
            self.request,
            "Corrección guardada. El registro anterior se conserva como respaldo.",
        )
        return redirect("care:record_detail", pk=new_record.pk)


class DailyCareRecordReviewView(RoleRequiredMixin, View):
    allowed_roles = (Role.ENFERMERIA,)

    def post(self, request, pk, *args, **kwargs):
        record = get_object_or_404(
            DailyCareRecord.objects.select_related("resident"), pk=pk
        )
        if not record.resident.is_active:
            messages.warning(
                request,
                "La ficha está archivada. Reactívala antes de revisar el registro.",
            )
            return redirect("care:record_detail", pk=record.pk)
        if record.status != DailyCareRecord.Status.VIGENTE:
            messages.warning(
                request,
                "No se puede revisar un registro corregido. Abre la versión vigente.",
            )
            return redirect("care:record_detail", pk=record.pk)
        if record.reviewed_at:
            messages.info(request, "Este registro ya fue revisado.")
            return redirect("care:record_detail", pk=record.pk)
        if not record.requires_nursing_review:
            messages.info(
                request,
                "Este registro no está marcado para revisión de Enfermería.",
            )
            return redirect("care:record_detail", pk=record.pk)

        notes = (request.POST.get("review_notes") or "").strip()
        if len(notes) > 1000:
            messages.error(
                request,
                "Las observaciones de la revisión no pueden superar los 1000 caracteres.",
            )
            return redirect("care:record_detail", pk=record.pk)

        record.reviewed_by = request.user
        record.reviewed_at = timezone.now()
        record.review_notes = notes
        record._audit_action = AuditLog.Action.REVIEW
        record.save(
            update_fields=[
                "reviewed_by",
                "reviewed_at",
                "review_notes",
                "updated_by",
                "updated_at",
            ]
        )
        messages.success(request, "Registro revisado por Enfermería.")
        return redirect("care:record_detail", pk=record.pk)


class DailyCareRecordExportView(RoleRequiredMixin, View):
    allowed_roles = (Role.DIRECCION, Role.ENFERMERIA)

    def get(self, request, *args, **kwargs):
        queryset = DailyCareRecord.objects.select_related(
            "resident", "care_plan", "created_by", "reviewed_by"
        )
        fecha = request.GET.get("fecha", "").strip()
        show_all_dates = fecha == "todas" or request.GET.get("todas") in {"1", "true", "on"}
        target_date = None
        if not show_all_dates:
            try:
                target_date = date.fromisoformat(fecha) if fecha else timezone.localdate()
            except ValueError:
                target_date = timezone.localdate()
            queryset = queryset.filter(recorded_at__date=target_date)

        shift = request.GET.get("turno", "").strip()
        if shift in DailyCareRecord.Shift.values:
            queryset = queryset.filter(shift=shift)

        category = request.GET.get("categoria", "").strip()
        if category in DailyCareRecord.Category.values:
            queryset = queryset.filter(category=category)

        resident_id = request.GET.get("residente", "").strip()
        if resident_id.isdigit():
            queryset = queryset.filter(resident_id=resident_id)

        query = request.GET.get("q", "").strip()
        if query:
            compact = query.replace(".", "").replace(" ", "")
            queryset = queryset.filter(
                Q(resident__first_name__icontains=query)
                | Q(resident__last_name__icontains=query)
                | Q(resident__preferred_name__icontains=query)
                | Q(resident__rut__icontains=compact)
                | Q(description__icontains=query)
            )

        only_pending = request.GET.get("pendientes") in {"1", "true", "on"}
        if only_pending:
            queryset = queryset.filter(
                requires_nursing_review=True, reviewed_at__isnull=True
            )

        include_corrected = request.GET.get("corregidos") in {"1", "true", "on"}
        if not include_corrected:
            queryset = queryset.filter(status=DailyCareRecord.Status.VIGENTE)

        records_list = list(queryset.order_by("-recorded_at", "-pk"))

        log_action(
            action=AuditLog.Action.EXPORT,
            actor=request.user,
            model_label="care.DailyCareRecord",
            object_repr=f"Registros de cuidados ({len(records_list)} registros)",
            changes={
                "filtros": {
                    "fecha": fecha,
                    "turno": shift,
                    "categoria": category,
                    "residente": resident_id,
                    "q": query,
                    "pendientes": only_pending,
                    "corregidos": include_corrected,
                },
                "total": len(records_list),
            },
        )

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        filename = f"registros_cuidados_{timezone.now():%Y%m%d_%H%M}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write("\ufeff")

        writer = csv.writer(response)
        writer.writerow([
            "ID",
            "Fecha y hora",
            "Turno",
            "RUT Residente",
            "Residente",
            "Categoría",
            "Descripción",
            "Observaciones",
            "Requiere revisión",
            "Revisado",
            "Fecha revisión",
            "Revisor",
            "Observaciones revisión",
            "Registrado por",
            "Estado",
        ])

        for rec in records_list:
            writer.writerow([
                rec.pk,
                rec.recorded_at.strftime("%d/%m/%Y %H:%M") if rec.recorded_at else "",
                rec.get_shift_display(),
                rec.resident.rut_formatted,
                rec.resident.get_full_name(),
                rec.get_category_display(),
                rec.description,
                rec.notes or "",
                "Sí" if rec.requires_nursing_review else "No",
                "Sí" if rec.reviewed_at else "No",
                rec.reviewed_at.strftime("%d/%m/%Y %H:%M") if rec.reviewed_at else "",
                rec.reviewed_by.get_full_name() if rec.reviewed_by else "",
                rec.review_notes or "",
                rec.created_by.get_full_name() if rec.created_by else "",
                rec.get_status_display(),
            ])

        return response
