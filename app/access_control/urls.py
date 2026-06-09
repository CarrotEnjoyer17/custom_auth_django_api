from django.urls import path

from access_control.views import (
    AccessRoleRuleDetailView,
    AccessRoleRuleListView,
    BusinessElementListView,
    RoleListView,
)


urlpatterns = [
    path("roles/", RoleListView.as_view(), name="access-roles"),
    path("elements/", BusinessElementListView.as_view(), name="access-elements"),
    path("rules/", AccessRoleRuleListView.as_view(), name="access-rules"),
    path("rules/<int:rule_id>/", AccessRoleRuleDetailView.as_view(), name="access-rule-detail"),
]