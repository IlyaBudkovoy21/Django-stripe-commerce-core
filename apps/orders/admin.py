from django.contrib import admin

from .models import Discount, Order, OrderItem, Tax


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "currency", "discount", "tax", "total_amount", "created_at")
    list_filter = ("status", "currency", "discount", "tax")
    search_fields = ("id",)
    inlines = [OrderItemInline]
    readonly_fields = ("total_amount", "created_at", "updated_at")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "item", "quantity")
    list_filter = ("item",)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "percent_off", "is_active", "stripe_coupon_id")
    list_filter = ("is_active",)
    search_fields = ("name", "stripe_coupon_id")


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "percentage", "inclusive", "is_active", "stripe_tax_rate_id")
    list_filter = ("inclusive", "is_active")
    search_fields = ("name", "stripe_tax_rate_id")
