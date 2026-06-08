from django.urls import path

from auth_system.views import RegisterView, LoginView, AuthMeView, LogoutView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", AuthMeView.as_view(), name="auth-me"),
    path("logout/", LogoutView.as_view(), name="logout")
]