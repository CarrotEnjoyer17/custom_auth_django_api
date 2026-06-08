from django.contrib import admin

from users.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "first_name", "last_name", "is_active", "created_at",)
    search_fields = ("email", "first_name", "last_name",)
    list_filter = ("is_active",)