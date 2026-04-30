from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "currency", "total_amount", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("id",)
    inlines = [OrderItemInline]
    readonly_fields = ("total_amount", "created_at", "updated_at")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "item", "quantity")
    list_filter = ("item",)
