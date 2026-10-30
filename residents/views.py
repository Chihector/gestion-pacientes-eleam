from __future__ import annotations

import csv

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.models import Role
from audit.models import AuditLog
from audit.services import log_action
from care.models import CarePlan, DailyCareRecord
from core.mixins import RoleRequiredMixin

from .forms import ContactForm, ResidentAdminForm, ResidentClinicalForm
from .models import Contact, Resident


class ResidentListView(LoginRequiredMixin, ListView):
    model = Resident
    template_name = "residents/resident_list.html"
    context_object_name = "residents"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            Resident.objects.select_related("updated_by")
            .prefetch_related(
                Prefetch(
                    "contacts",
                    queryset=Contact.objects.filter(is_primary=True),
                    to_attr="primary_contacts",
                )
            )
        )

        query = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("estado", "").strip()
        include_archived = self.request.GET.get("archivados") in {
            "1",
            "true",
            "on",
        }

        if not include_archived:
            queryset = queryset.filter(is_active=True)
        if status in Resident.Status.values:
            queryset = queryset.filter(status=status)
        if query:
            compact = query.replace(".", "").replace(" ", "")
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(preferred_name__icontains=query)
                | Q(room__icontains=query)
                | Q(rut__icontains=compact)
            )
        return queryset

    def get_template_names(self):
        if self.request.headers.get("HX-Request") == "true":
            return ["residents/_results.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["estado"] = self.request.GET.get("estado", "")
        context["incluir_archivados"] = self.request.GET.get("archivados") in {
            "1",
            "true",
            "on",
        }
        context["total"] = self.get_queryset().count()
        context["statuses"] = Resident.Status.choices
        context["can_create"] = self.request.user.can_edit_resident_admin
        context["can_export"] = self.request.user.can_export_residents
        return context


class ResidentDetailView(LoginRequiredMixin, DetailView):
    model = Resident
    template_name = "residents/resident_detail.html"
    context_object_name = "resident"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resident = self.object
        contacts = resident.contacts.all()
        context["contacts"] = contacts
        context["primary_contact"] = contacts.filter(is_primary=True).first()
        context["can_edit_admin"] = self.request.user.can_edit_resident_admin
        context["can_edit_clinical"] = self.request.user.can_edit_resident_clinical
        context["can_manage_contacts"] = self.request.user.can_manage_contacts
        context["can_archive"] = self.request.user.can_archive_residents
        context["is_archived"] = not resident.is_active
        context["can_view_audit"] = self.request.user.can_view_audit

        care_plans = resident.care_plans.select_related("responsible").order_by(
            "status", "-start_date", "-pk"
        )
        context["care_plans"] = care_plans
        context["active_care_plans"] = [
            plan for plan in care_plans if plan.status == CarePlan.Status.ACTIVO
        ]
        context["closed_care_plans"] = [
            plan for plan in care_plans if plan.status == CarePlan.Status.CERRADO
        ]
        context["recent_care_records"] = resident.daily_records.select_related(
            "created_by"
        ).filter(status=DailyCareRecord.Status.VIGENTE)[:8]
        context["care_record_count"] = resident.daily_records.filter(
            status=DailyCareRecord.Status.VIGENTE
        ).count()
        context["care_pending_review"] = resident.daily_records.filter(
            status=DailyCareRecord.Status.VIGENTE,
            requires_nursing_review=True,
            reviewed_at__isnull=True,
        ).count()
        context["can_manage_care"] = self.request.user.can_manage_care_plans
        context["can_record_care"] = self.request.user.can_record_care

        if self.request.user.can_view_audit:
            contact_ids = [str(pk) for pk in contacts.values_list("pk", flat=True)]
            query = Q(model_label="residents.Resident", object_id=str(resident.pk))
            if contact_ids:
                query |= Q(
                    model_label="residents.Contact", object_id__in=contact_ids
                )
            context["audit_logs"] = (
                AuditLog.objects.filter(query)
                .select_related("actor")
                .order_by("-created_at")[:10]
            )
        return context


class ResidentCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = (Role.ENFERMERIA, Role.ADMINISTRACION)
    model = Resident
    form_class = ResidentAdminForm
    template_name = "residents/resident_form.html"
    extra_context = {
        "title": "Nuevo residente",
        "subtitle": "Completa los datos administrativos. La información clínica se registra después, solo con Enfermería.",
        "submit_label": "Crear ficha",
    }

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Ficha creada. La información clínica puede completarse por Enfermería.",
        )
        return response


class ActiveResidentRequiredMixin:
    """Impide editar fichas archivadas hasta reactivarlas."""

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        resident = getattr(self.object, "resident", None)
        if self.object is not None and hasattr(self.object, "is_active"):
            resident = self.object
        if resident is not None and not resident.is_active:
            messages.warning(
                request,
                "La ficha está archivada. Reactívala antes de modificarla.",
            )
            return redirect("residents:detail", pk=resident.pk)
        return super().dispatch(request, *args, **kwargs)


class ResidentUpdateView(
    RoleRequiredMixin, ActiveResidentRequiredMixin, UpdateView
):
    allowed_roles = (Role.ENFERMERIA, Role.ADMINISTRACION)
    model = Resident
    form_class = ResidentAdminForm
    template_name = "residents/resident_form.html"
    extra_context = {
        "title": "Editar datos administrativos",
        "subtitle": "Solo se modifican datos administrativos. Las alergias y antecedentes tienen su propio formulario.",
        "submit_label": "Guardar cambios",
    }

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Datos administrativos actualizados.")
        return response


class ResidentClinicalUpdateView(
    RoleRequiredMixin, ActiveResidentRequiredMixin, UpdateView
):
    allowed_roles = (Role.ENFERMERIA,)
    model = Resident
    form_class = ResidentClinicalForm
    template_name = "residents/resident_form.html"
    extra_context = {
        "title": "Editar información clínica",
        "subtitle": "Solo Enfermería puede modificar alergias, antecedentes y observaciones.",
        "submit_label": "Guardar información clínica",
        "clinical": True,
    }

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Información clínica actualizada.")
        return response


class ResidentArchiveView(RoleRequiredMixin, View):
    allowed_roles = (Role.ENFERMERIA, Role.ADMINISTRACION)

    def post(self, request, pk, *args, **kwargs):
        resident = get_object_or_404(Resident, pk=pk)
        resident.is_active = not resident.is_active
        resident._audit_action = (
            AuditLog.Action.RESTORE if resident.is_active else AuditLog.Action.ARCHIVE
        )
        resident.save()
        if resident.is_active:
            messages.success(request, "Ficha reactivada.")
        else:
            messages.success(
                request,
                "Ficha archivada. Sus datos y su historial se conservan.",
            )
        return redirect("residents:detail", pk=resident.pk)


class ContactCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = (Role.ENFERMERIA, Role.ADMINISTRACION)
    model = Contact
    form_class = ContactForm
    template_name = "residents/contact_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.resident = get_object_or_404(Resident, pk=kwargs["resident_pk"])
        if not self.resident.is_active:
            messages.warning(
                request,
                "La ficha está archivada. Reactívala antes de modificar sus contactos.",
            )
            return redirect("residents:detail", pk=self.resident.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["resident"] = self.resident
        context["title"] = "Agregar contacto"
        context["submit_label"] = "Guardar contacto"
        return context

    def form_valid(self, form):
        form.instance.resident = self.resident
        response = super().form_valid(form)
        messages.success(self.request, "Contacto agregado.")
        return response

    def get_success_url(self):
        return reverse("residents:detail", kwargs={"pk": self.resident.pk})


class ContactUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = (Role.ENFERMERIA, Role.ADMINISTRACION)
    model = Contact
    form_class = ContactForm
    template_name = "residents/contact_form.html"
    context_object_name = "contact"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.resident = self.object.resident
        if not self.resident.is_active:
            messages.warning(
                request,
                "La ficha está archivada. Reactívala antes de modificar sus contactos.",
            )
            return redirect("residents:detail", pk=self.resident.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["resident"] = self.resident
        context["title"] = "Editar contacto"
        context["submit_label"] = "Guardar cambios"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Contacto actualizado.")
        return response

    def get_success_url(self):
        return reverse("residents:detail", kwargs={"pk": self.resident.pk})


class ContactDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = (Role.ENFERMERIA, Role.ADMINISTRACION)
    model = Contact
    template_name = "residents/contact_confirm_delete.html"
    context_object_name = "contact"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.resident = self.object.resident
        if not self.resident.is_active:
            messages.warning(
                request,
                "La ficha está archivada. Reactívala antes de modificar sus contactos.",
            )
            return redirect("residents:detail", pk=self.resident.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["resident"] = self.resident
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Contacto eliminado. La acción quedó registrada en la auditoría.",
        )
        return response

    def get_success_url(self):
        return reverse("residents:detail", kwargs={"pk": self.resident.pk})


class ResidentExportView(RoleRequiredMixin, View):
    allowed_roles = (Role.DIRECCION, Role.ADMINISTRACION, Role.ENFERMERIA)

    def get(self, request, *args, **kwargs):
        queryset = (
            Resident.objects.select_related("updated_by")
            .prefetch_related(
                Prefetch(
                    "contacts",
                    queryset=Contact.objects.filter(is_primary=True),
                    to_attr="primary_contacts",
                )
            )
        )

        query = request.GET.get("q", "").strip()
        status = request.GET.get("estado", "").strip()
        include_archived = request.GET.get("archivados") in {
            "1",
            "true",
            "on",
        }

        if not include_archived:
            queryset = queryset.filter(is_active=True)
        if status in Resident.Status.values:
            queryset = queryset.filter(status=status)
        if query:
            compact = query.replace(".", "").replace(" ", "")
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(preferred_name__icontains=query)
                | Q(room__icontains=query)
                | Q(rut__icontains=compact)
            )

        residents_list = list(queryset.order_by("last_name", "first_name"))

        log_action(
            action=AuditLog.Action.EXPORT,
            actor=request.user,
            model_label="residents.Resident",
            object_repr=f"Nómina de residentes ({len(residents_list)} registros)",
            changes={
                "filtros": {
                    "q": query,
                    "estado": status,
                    "incluir_archivados": include_archived,
                },
                "total": len(residents_list),
            },
        )

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        filename = f"nomina_residentes_{timezone.now():%Y%m%d_%H%M}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.write("\ufeff")

        writer = csv.writer(response)
        writer.writerow([
            "RUT",
            "Nombres",
            "Apellidos",
            "Nombre preferido",
            "Fecha de nacimiento",
            "Edad",
            "Sexo",
            "Habitación",
            "Previsión",
            "Estado",
            "Fecha de ingreso",
            "Contacto principal",
            "Parentesco",
            "Teléfono contacto",
        ])

        for r in residents_list:
            primary = r.primary_contacts[0] if getattr(r, "primary_contacts", None) else None
            writer.writerow([
                r.rut_formatted,
                r.first_name,
                r.last_name,
                r.preferred_name or "",
                r.birth_date.strftime("%d/%m/%Y") if r.birth_date else "",
                r.age if r.birth_date else "",
                r.get_sex_display(),
                r.room or "",
                r.get_health_insurance_display(),
                r.get_status_display(),
                r.admission_date.strftime("%d/%m/%Y") if r.admission_date else "",
                primary.name if primary else "",
                primary.relationship if primary else "",
                primary.phone if primary else "",
            ])

        return response
