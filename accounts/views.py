from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from audit.models import AuditLog
from audit.services import log_action
from core.mixins import RoleRequiredMixin

from .forms import (
    AdminPasswordResetForm,
    LoginForm,
    StyledPasswordChangeForm,
    UserCreateForm,
    UserUpdateForm,
)
from .models import Role, User


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class UserPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = StyledPasswordChangeForm
    success_url = reverse_lazy("core:dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(
            action=AuditLog.Action.PASSWORD,
            actor=self.request.user,
            instance=self.request.user,
            changes={},
        )
        messages.success(self.request, "Tu contraseña fue actualizada.")
        return response


class UserListView(RoleRequiredMixin, ListView):
    allowed_roles = (Role.ADMINISTRACION,)
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        role = self.request.GET.get("rol", "").strip()
        if query:
            queryset = queryset.filter(
                Q(email__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )
        if role in Role.values:
            queryset = queryset.filter(role=role)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["roles"] = Role.choices
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "rol": self.request.GET.get("rol", ""),
        }
        context["active_count"] = User.objects.filter(is_active=True).count()
        context["inactive_count"] = User.objects.filter(is_active=False).count()
        context["admin_count"] = User.objects.filter(
            is_active=True, role=Role.ADMINISTRACION
        ).count()
        return context


class UserCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = (Role.ADMINISTRACION,)
    model = User
    form_class = UserCreateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")
    extra_context = {"title": "Nuevo usuario", "submit_label": "Crear cuenta"}

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Cuenta de {self.object.get_full_name()} creada. Pídele cambiar la contraseña al ingresar.",
        )
        return response


class UserUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = (Role.ADMINISTRACION,)
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")
    extra_context = {"title": "Editar usuario", "submit_label": "Guardar cambios"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["actor"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f"Cuenta de {self.object.get_full_name()} actualizada."
        )
        return response


class UserPasswordResetView(RoleRequiredMixin, View):
    allowed_roles = (Role.ADMINISTRACION,)
    template_name = "accounts/user_password_reset.html"

    def get_target(self):
        return get_object_or_404(User, pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        target = self.get_target()
        form = AdminPasswordResetForm(user=target)
        return render(
            request, self.template_name, {"form": form, "target": target}
        )

    def post(self, request, *args, **kwargs):
        target = self.get_target()
        form = AdminPasswordResetForm(request.POST, user=target)
        if form.is_valid():
            form.save()
            log_action(
                action=AuditLog.Action.PASSWORD_RESET,
                actor=request.user,
                instance=target,
                changes={},
            )
            messages.success(
                request,
                f"Contraseña de {target.get_full_name()} restablecida. Pídele cambiarla al ingresar.",
            )
            return redirect("accounts:user_list")
        return render(
            request, self.template_name, {"form": form, "target": target}
        )
