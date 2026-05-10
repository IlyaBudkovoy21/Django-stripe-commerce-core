from django.contrib import admin
from django.utils.html import format_html

from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "currency", "checkout_link", "intent_link", "created_at")
    list_filter = ("currency",)
    search_fields = ("name", "description")
    ordering = ("id",)

    @admin.display(description="Checkout")
    def checkout_link(self, obj):
        return format_html('<a href="/item/{}/" target="_blank">Open</a>', obj.id)

    @admin.display(description="Payment Intent")
    def intent_link(self, obj):
        return format_html('<a href="/item/{}/intent/" target="_blank">Open</a>', obj.id)
