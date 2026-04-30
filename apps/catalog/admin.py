from django.contrib import admin

from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "currency", "created_at")
    list_filter = ("currency",)
    search_fields = ("name", "description")
    ordering = ("id",)
