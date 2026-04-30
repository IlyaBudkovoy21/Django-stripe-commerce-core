from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import stripe

from apps.orders.models import Order


def _configure_stripe() -> None:
    if not settings.STRIPE_SECRET_KEY:
        raise ImproperlyConfigured("STRIPE_SECRET_KEY is not configured")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe.api_version = settings.STRIPE_API_VERSION


def create_item_checkout_session(*, item_id: int, item_name: str, amount: int, item_description: str):
    _configure_stripe()

    return stripe.checkout.Session.create(
        mode="payment",
        success_url=f"{settings.APP_BASE_URL}/item/{item_id}/",
        cancel_url=f"{settings.APP_BASE_URL}/item/{item_id}/",
        line_items=[
            {
                "quantity": 1,
                "price_data": {
                    "currency": settings.STRIPE_DEFAULT_CURRENCY,
                    "unit_amount": amount,
                    "product_data": {
                        "name": item_name,
                        "description": item_description,
                    },
                },
            }
        ],
    )


def create_order_checkout_session(*, order: Order):
    _configure_stripe()

    order_items = list(order.order_items.select_related("item"))
    if not order_items:
        raise ValueError("Order is empty")

    line_items = [
        {
            "quantity": order_item.quantity,
            "price_data": {
                "currency": order.currency.lower(),
                "unit_amount": order_item.item.price,
                "product_data": {
                    "name": order_item.item.name,
                    "description": order_item.item.description,
                },
            },
        }
        for order_item in order_items
    ]

    return stripe.checkout.Session.create(
        mode="payment",
        success_url=f"{settings.APP_BASE_URL}/admin/orders/order/{order.id}/change/",
        cancel_url=f"{settings.APP_BASE_URL}/admin/orders/order/{order.id}/change/",
        line_items=line_items,
        metadata={"order_id": str(order.id)},
    )
