from django.urls import path

from users.views import UserMeView


urlpatterns = [
    path("me/", UserMeView.as_view(), name="user-me"),
]