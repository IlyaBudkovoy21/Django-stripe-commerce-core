from django.core.management.base import BaseCommand

from apps.catalog.models import Item
from apps.orders.models import Discount, Order, OrderItem, Tax


class Command(BaseCommand):
    help = "Create demo data for quick payment flow testing"

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        discount, _ = Discount.objects.get_or_create(
            name="Spring Sale",
            defaults={"percent_off": "10.00", "is_active": True},
        )
        tax, _ = Tax.objects.get_or_create(
            name="Sales Tax",
            defaults={"percentage": "7.50", "inclusive": False, "is_active": True},
        )

        usd_items = [
            {
                "name": "Python Course",
                "description": "Hands-on Python engineering course",
                "price": 12900,
                "currency": Item.Currency.USD,
            },
            {
                "name": "Django Template Pack",
                "description": "Production-ready Django project templates",
                "price": 5900,
                "currency": Item.Currency.USD,
            },
        ]

        eur_items = [
            {
                "name": "Architecture Review",
                "description": "System design and scalability review session",
                "price": 8900,
                "currency": Item.Currency.EUR,
            },
            {
                "name": "Code Quality Audit",
                "description": "Automated and manual review of code quality",
                "price": 7600,
                "currency": Item.Currency.EUR,
            },
        ]

        created_items = []
        for payload in usd_items + eur_items:
            item, _ = Item.objects.get_or_create(
                name=payload["name"],
                defaults={
                    "description": payload["description"],
                    "price": payload["price"],
                    "currency": payload["currency"],
                },
            )
            created_items.append(item)

        usd_order, _ = Order.objects.get_or_create(
            currency=Item.Currency.USD,
            discount=discount,
            tax=tax,
            status=Order.Status.DRAFT,
        )
        OrderItem.objects.get_or_create(order=usd_order, item=created_items[0], defaults={"quantity": 1})
        OrderItem.objects.get_or_create(order=usd_order, item=created_items[1], defaults={"quantity": 2})
        usd_order.refresh_total_amount()

        eur_order, _ = Order.objects.get_or_create(
            currency=Item.Currency.EUR,
            status=Order.Status.DRAFT,
        )
        OrderItem.objects.get_or_create(order=eur_order, item=created_items[2], defaults={"quantity": 1})
        OrderItem.objects.get_or_create(order=eur_order, item=created_items[3], defaults={"quantity": 1})
        eur_order.refresh_total_amount()

        self.stdout.write(self.style.SUCCESS("Demo data is ready"))
