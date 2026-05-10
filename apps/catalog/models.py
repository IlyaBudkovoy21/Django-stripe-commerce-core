from django.conf import settings
from django.db import models


class Item(models.Model):
    class Currency(models.TextChoices):
        USD = "USD", "USD"
        EUR = "EUR", "EUR"

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.PositiveIntegerField(help_text="Price in smallest currency unit")
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=settings.STRIPE_DEFAULT_CURRENCY.upper(),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.price} {self.currency})"
