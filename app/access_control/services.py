from access_control.models import AccessRoleRule


def has_permission(user, element_code, action):
    if user is None or not user.is_active:
        return False
    

    rules = AccessRoleRule.objects.filter(
        role__user_roles__user=user,
        element__code=element_code,
    )

    if action == "read":
        return rules.filter(read_permission=True).exists()

    if action == "read_all":
        return rules.filter(read_all_permission=True).exists()

    if action == "create":
        return rules.filter(create_permission=True).exists()

    if action == "update":
        return rules.filter(update_permission=True).exists()

    if action == "update_all":
        return rules.filter(update_all_permission=True).exists()

    if action == "delete":
        return rules.filter(delete_permission=True).exists()

    if action == "delete_all":
        return rules.filter(delete_all_permission=True).exists()

    return False