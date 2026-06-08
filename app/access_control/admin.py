from django.contrib import admin

from access_control.models import Role, UserRole, BusinessElement, AccessRoleRule


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.register(UserRole)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role")
    search_fields = ("user__email", "role__code")


@admin.register(BusinessElement)
class BusinessElementAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")



@admin.register(AccessRoleRule)
class AccessRoleRuleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "role",
        "element",
        "read_permission",
        "read_all_permission",
        "create_permission",
        "update_permission",
        "update_all_permission",
        "delete_permission",
        "delete_all_permission",
    )
    list_filter = ("role", "element")