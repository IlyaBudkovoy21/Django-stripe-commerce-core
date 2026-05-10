from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings

import stripe

from apps.orders.models import Discount, Order, Tax

from .keys import get_stripe_secret_key_for_currency


def _configure_stripe(currency: str) -> None:
    stripe.api_key = get_stripe_secret_key_for_currency(currency)
    stripe.api_version = settings.STRIPE_API_VERSION


def create_item_checkout_session(*, item_id: int, item_name: str, amount: int, item_description: str, currency: str):
    _configure_stripe(currency)

    return stripe.checkout.Session.create(
        mode="payment",
        success_url=f"{settings.APP_BASE_URL}/item/{item_id}/",
        cancel_url=f"{settings.APP_BASE_URL}/item/{item_id}/",
        line_items=[
            {
                "quantity": 1,
                "price_data": {
                    "currency": currency.lower(),
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
    _configure_stripe(order.currency)

    order_items = list(order.order_items.select_related("item"))
    if not order_items:
        raise ValueError("Order is empty")

    stripe_coupon_id = _get_or_create_coupon(order.discount) if order.discount and order.discount.is_active else None
    stripe_tax_rate_id = _get_or_create_tax_rate(order.tax) if order.tax and order.tax.is_active else None

    line_items = []
    for order_item in order_items:
        line_item = {
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
        if stripe_tax_rate_id:
            line_item["tax_rates"] = [stripe_tax_rate_id]
        line_items.append(line_item)

    payload = {
        "mode": "payment",
        "success_url": f"{settings.APP_BASE_URL}/admin/orders/order/{order.id}/change/",
        "cancel_url": f"{settings.APP_BASE_URL}/admin/orders/order/{order.id}/change/",
        "line_items": line_items,
        "metadata": {"order_id": str(order.id)},
    }
    if stripe_coupon_id:
        payload["discounts"] = [{"coupon": stripe_coupon_id}]

    return stripe.checkout.Session.create(**payload)


def _get_or_create_coupon(discount: Discount) -> str:
    if discount.stripe_coupon_id:
        return discount.stripe_coupon_id

    coupon = stripe.Coupon.create(
        name=discount.name,
        duration="once",
        percent_off=float(discount.percent_off),
    )
    discount.stripe_coupon_id = coupon.id
    discount.save(update_fields=["stripe_coupon_id", "updated_at"])
    return coupon.id


def _get_or_create_tax_rate(tax: Tax) -> str:
    if tax.stripe_tax_rate_id:
        return tax.stripe_tax_rate_id

    tax_rate = stripe.TaxRate.create(
        display_name=tax.name,
        percentage=float(tax.percentage),
        inclusive=tax.inclusive,
        jurisdiction="Global",
    )
    tax.stripe_tax_rate_id = tax_rate.id
    tax.save(update_fields=["stripe_tax_rate_id", "updated_at"])
    return tax_rate.id


def create_item_payment_intent(*, item_id: int, amount: int, currency: str):
    _configure_stripe(currency)
    return stripe.PaymentIntent.create(
        amount=amount,
        currency=currency.lower(),
        automatic_payment_methods={"enabled": True},
        metadata={"item_id": str(item_id)},
    )


def create_order_payment_intent(*, order: Order):
    _configure_stripe(order.currency)

    amount = _calculate_order_amount_for_payment_intent(order)
    if amount < 1:
        raise ValueError("Calculated order amount must be greater than 0")

    return stripe.PaymentIntent.create(
        amount=amount,
        currency=order.currency.lower(),
        automatic_payment_methods={"enabled": True},
        metadata={"order_id": str(order.id)},
    )


def _calculate_order_amount_for_payment_intent(order: Order) -> int:
    amount = Decimal(order.calculate_total_amount())
    if amount < 1:
        raise ValueError("Order is empty")

    if order.discount and order.discount.is_active:
        discount_ratio = Decimal("1") - (Decimal(order.discount.percent_off) / Decimal("100"))
        amount = amount * discount_ratio

    if order.tax and order.tax.is_active:
        tax_ratio = Decimal("1") + (Decimal(order.tax.percentage) / Decimal("100"))
        amount = amount * tax_ratio

    return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
