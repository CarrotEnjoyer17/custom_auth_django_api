from django.core.management.base import BaseCommand
from users.models import User
from access_control.models import Role, UserRole


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(email="product_user_new@example.com")
        admin_role = Role.objects.get(code="admin")

        UserRole.objects.get_or_create(user=user, role=admin_role)
        
        self.stdout.write(
            self.style.SUCCESS("Admin role sccessfully added to example user")
        )