from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import stripe


def create_item_checkout_session(*, item_id: int, item_name: str, amount: int, item_description: str):
    if not settings.STRIPE_SECRET_KEY:
        raise ImproperlyConfigured("STRIPE_SECRET_KEY is not configured")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe.api_version = settings.STRIPE_API_VERSION

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
