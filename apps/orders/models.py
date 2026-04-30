from django.conf import settings
from django.db import models

from apps.catalog.models import Item


class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PAID = "paid", "Paid"
        CANCELED = "canceled", "Canceled"

    currency = models.CharField(max_length=3, default=settings.STRIPE_DEFAULT_CURRENCY.upper())
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    items = models.ManyToManyField(Item, through="OrderItem", related_name="orders")
    total_amount = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.id}"

    def calculate_total_amount(self) -> int:
        return sum(order_item.line_total for order_item in self.order_items.select_related("item"))

    def refresh_total_amount(self, *, save: bool = True) -> int:
        self.total_amount = self.calculate_total_amount()
        if save:
            self.save(update_fields=["total_amount", "updated_at"])
        return self.total_amount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("order", "item")

    def __str__(self) -> str:
        return f"Order #{self.order_id}: {self.item.name} x{self.quantity}"

    @property
    def line_total(self) -> int:
        return self.item.price * self.quantity

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.refresh_total_amount()

    def delete(self, *args, **kwargs):
        order = self.order
        result = super().delete(*args, **kwargs)
        order.refresh_total_amount()
        return result
