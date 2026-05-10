from django.contrib import admin
from django.utils.html import format_html

from .models import Discount, Order, OrderItem, Tax


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "currency",
        "discount",
        "tax",
        "total_amount",
        "checkout_api_link",
        "intent_api_link",
        "created_at",
    )
    list_filter = ("status", "currency", "discount", "tax")
    search_fields = ("id",)
    inlines = [OrderItemInline]
    readonly_fields = ("total_amount", "created_at", "updated_at")
    actions = ["recalculate_totals"]

    @admin.display(description="Checkout API")
    def checkout_api_link(self, obj):
        return format_html('<a href="/buy/order/{}/" target="_blank">Call</a>', obj.id)

    @admin.display(description="Intent API")
    def intent_api_link(self, obj):
        return format_html('<a href="/pay-intent/order/{}/" target="_blank">Call</a>', obj.id)

    @admin.action(description="Recalculate totals")
    def recalculate_totals(self, request, queryset):
        for order in queryset:
            order.refresh_total_amount()
        self.message_user(request, f"Recalculated totals for {queryset.count()} order(s)")


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
