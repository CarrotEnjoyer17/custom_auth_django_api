from django.core.management.base import BaseCommand

from access_control.models import Role, BusinessElement, AccessRoleRule


class Command(BaseCommand):
    help = "Seed roles, business elements and default access rules"

    def handle(self, *args, **options):
        roles = [
            ("admin", "Admin"),
            ("manager", "Manager"),
            ("user", "User"),
            ("guest", "Guest")
        ]

        elements = [
            ("users", "Users"),
            ("products", "Products"),
            ("orders", "Orders"),
            ("shops", "Shops"),
            ("access_rules", "Access rules")
        ]

        for code, name in roles:
            Role.objects.get_or_create(
                code=code,
                defaults={"name": name},
            )

        for code, name in elements:
            BusinessElement.objects.get_or_create(
                code=code,
                defaults={"name": name},
            )

        admin_role = Role.objects.get(code="admin")

        for element in BusinessElement.objects.all():
            AccessRoleRule.objects.update_or_create(
                role=admin_role,
                element=element,
                defaults={
                    "read_permission": True,
                    "read_all_permission": True,
                    "create_permission": True,
                    "update_permission": True,
                    "update_all_permission": True,
                    "delete_permission": True,
                    "delete_all_permission": True,
                },
            )
        
        user_role = Role.objects.get(code="user")
        manager_role = Role.objects.get(code="manager")
        guest_role = Role.objects.get(code="guest")

        business_elements = BusinessElement.objects.filter(
            code__in=["products", "orders", "shops"]
        )

        for element in business_elements:
            AccessRoleRule.objects.update_or_create(
                role=user_role,
                element=element,
                defaults={
                    "read_permission": True,
                    "read_all_permission": False,
                    "create_permission": True,
                    "update_permission": True,
                    "update_all_permission": False,
                    "delete_permission": False,
                    "delete_all_permission": False,
                },
            )

            AccessRoleRule.objects.update_or_create(
                role=manager_role,
                element=element,
                defaults={
                    "read_permission": True,
                    "read_all_permission": True,
                    "create_permission": True,
                    "update_permission": True,
                    "update_all_permission": True,
                    "delete_permission": True,
                    "delete_all_permission": False,
                },
            )

            AccessRoleRule.objects.update_or_create(
                role=guest_role,
                element=element,
                defaults={
                    "read_permission": True,
                    "read_all_permission": False,
                    "create_permission": False,
                    "update_permission": False,
                    "update_all_permission": False,
                    "delete_permission": False,
                    "delete_all_permission": False,
                },
            )

        self.stdout.write(
            self.style.SUCCESS("Access control seed data created successfully")
        )