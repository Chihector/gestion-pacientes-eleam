from __future__ import annotations

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q

from core.forms import BootstrapFormMixin

from .models import Role, User, active_admin_count


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "autofocus": True,
                "autocomplete": "username",
                "placeholder": "nombre@example.test",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "current-password",
            }
        ),
    )
    error_messages = {
        "invalid_login": "Correo o contraseña incorrectos. Revisa tus datos e inténtalo nuevamente.",
        "inactive": "Esta cuenta está desactivada. Contacta a Administración.",
    }


class UserCreateForm(BootstrapFormMixin, forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña inicial",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Mínimo 10 caracteres, no común y no solo numérica.",
    )
    password2 = forms.CharField(
        label="Repetir contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "role", "is_active"]
        labels = {
            "email": "Correo institucional",
            "first_name": "Nombre",
            "last_name": "Apellidos",
            "role": "Rol",
            "is_active": "Cuenta activa",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        if password1:
            try:
                validate_password(password1, self.instance)
            except ValidationError as error:
                self.add_error("password1", error)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "role", "is_active"]
        labels = {
            "email": "Correo institucional",
            "first_name": "Nombre",
            "last_name": "Apellidos",
            "role": "Rol",
            "is_active": "Cuenta activa",
        }

    def __init__(self, *args, actor=None, **kwargs):
        self.actor = actor
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        queryset = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean(self):
        cleaned = super().clean()
        if not self.instance.pk:
            return cleaned

        is_active = cleaned.get("is_active")
        new_role = cleaned.get("role")

        if self.instance == self.actor and not is_active:
            self.add_error("is_active", "No puedes desactivar tu propia cuenta.")

        loses_admin = self.instance.role == Role.ADMINISTRACION and (
            not is_active or new_role != Role.ADMINISTRACION
        )
        if loses_admin and not (self.instance.is_superuser and is_active):
            if active_admin_count(exclude_pk=self.instance.pk) == 0:
                self.add_error(
                    "role",
                    "Debe quedar al menos una cuenta activa con rol Administración o un superusuario activo.",
                )
        return cleaned


class StyledPasswordChangeForm(BootstrapFormMixin, PasswordChangeForm):
    pass


class AdminPasswordResetForm(BootstrapFormMixin, forms.Form):
    new_password1 = forms.CharField(
        label="Nueva contraseña temporal",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    new_password2 = forms.CharField(
        label="Repetir contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("new_password1")
        password2 = cleaned.get("new_password2")
        if password1 and password2 and password1 != password2:
            self.add_error("new_password2", "Las contraseñas no coinciden.")
        if password1 and self.user:
            try:
                validate_password(password1, self.user)
            except ValidationError as error:
                self.add_error("new_password1", error)
        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save(update_fields=["password", "updated_at"])
        return self.user


class AdminUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name", "role")


class AdminUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"
