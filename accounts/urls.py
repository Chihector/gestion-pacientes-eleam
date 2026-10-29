from django.urls import path

from .views import (
    UserCreateView,
    UserListView,
    UserLoginView,
    UserLogoutView,
    UserPasswordChangeView,
    UserPasswordResetView,
    UserUpdateView,
)

app_name = "accounts"

urlpatterns = [
    path("cuenta/login/", UserLoginView.as_view(), name="login"),
    path("cuenta/logout/", UserLogoutView.as_view(), name="logout"),
    path("cuenta/password/", UserPasswordChangeView.as_view(), name="password_change"),
    path("usuarios/", UserListView.as_view(), name="user_list"),
    path("usuarios/nuevo/", UserCreateView.as_view(), name="user_create"),
    path("usuarios/<int:pk>/editar/", UserUpdateView.as_view(), name="user_update"),
    path(
        "usuarios/<int:pk>/password/",
        UserPasswordResetView.as_view(),
        name="user_password_reset",
    ),
]
