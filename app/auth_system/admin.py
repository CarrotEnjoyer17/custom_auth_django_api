from django.contrib import admin

from auth_system.models import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "token_jti", "is_active", "created_at", "expires_at", "revoked_at")
    search_fields = ("user__email", "token_jti")
    list_filter = ("is_active",)