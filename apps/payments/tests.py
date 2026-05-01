from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from apps.catalog.models import Item
from apps.orders.models import Discount, Order, OrderItem, Tax
from apps.payments import services


class PaymentViewsTests(TestCase):
    def setUp(self):
        self.item = Item.objects.create(
            name="Test item",
            description="Test description",
            price=1500,
            currency=Item.Currency.USD,
        )

        self.order = Order.objects.create(currency=Item.Currency.USD)
        OrderItem.objects.create(order=self.order, item=self.item, quantity=2)

    @patch("apps.payments.views.create_item_checkout_session")
    def test_buy_item_returns_session_id(self, create_item_checkout_session_mock):
        create_item_checkout_session_mock.return_value = SimpleNamespace(id="cs_test_1")

        response = self.client.get(f"/buy/{self.item.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": "cs_test_1"})
        create_item_checkout_session_mock.assert_called_once_with(
            item_id=self.item.id,
            item_name=self.item.name,
            item_description=self.item.description,
            amount=self.item.price,
            currency=self.item.currency,
        )

    @patch("apps.payments.views.create_order_checkout_session")
    def test_buy_order_returns_session_id(self, create_order_checkout_session_mock):
        create_order_checkout_session_mock.return_value = SimpleNamespace(id="cs_test_order")

        response = self.client.get(f"/buy/order/{self.order.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": "cs_test_order"})
        create_order_checkout_session_mock.assert_called_once_with(order=self.order)

    @patch("apps.payments.views.create_item_payment_intent")
    def test_create_item_intent_returns_client_secret(self, create_item_payment_intent_mock):
        create_item_payment_intent_mock.return_value = SimpleNamespace(client_secret="pi_item_secret")

        response = self.client.get(f"/pay-intent/item/{self.item.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"client_secret": "pi_item_secret"})
        create_item_payment_intent_mock.assert_called_once_with(
            item_id=self.item.id,
            amount=self.item.price,
            currency=self.item.currency,
        )

    @patch("apps.payments.views.create_order_payment_intent")
    def test_create_order_intent_returns_client_secret(self, create_order_payment_intent_mock):
        create_order_payment_intent_mock.return_value = SimpleNamespace(client_secret="pi_order_secret")

        response = self.client.get(f"/pay-intent/order/{self.order.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"client_secret": "pi_order_secret"})
        create_order_payment_intent_mock.assert_called_once_with(order=self.order)


class PaymentServicesTests(TestCase):
    def setUp(self):
        self.item = Item.objects.create(
            name="Service item",
            description="Service description",
            price=5000,
            currency=Item.Currency.USD,
        )

    def test_calculate_order_amount_for_payment_intent_with_discount_and_tax(self):
        discount = Discount.objects.create(name="Discount 10", percent_off="10.00", is_active=True)
        tax = Tax.objects.create(name="Tax 7.5", percentage="7.50", is_active=True)
        order = Order.objects.create(currency=Item.Currency.USD, discount=discount, tax=tax)
        OrderItem.objects.create(order=order, item=self.item, quantity=2)

        amount = services._calculate_order_amount_for_payment_intent(order)

        self.assertEqual(amount, 9675)

    def test_calculate_order_amount_for_payment_intent_raises_for_empty_order(self):
        order = Order.objects.create(currency=Item.Currency.USD)

        with self.assertRaisesMessage(ValueError, "Order is empty"):
            services._calculate_order_amount_for_payment_intent(order)

    @patch("apps.payments.services._configure_stripe")
    @patch("apps.payments.services.stripe.checkout.Session.create")
    def test_create_order_checkout_session_includes_discount_tax_and_metadata(
        self,
        stripe_session_create_mock,
        configure_stripe_mock,
    ):
        discount = Discount.objects.create(
            name="Configured discount",
            percent_off="5.00",
            is_active=True,
            stripe_coupon_id="coupon_existing",
        )
        tax = Tax.objects.create(
            name="Configured tax",
            percentage="8.00",
            inclusive=False,
            is_active=True,
            stripe_tax_rate_id="tax_existing",
        )
        order = Order.objects.create(currency=Item.Currency.USD, discount=discount, tax=tax)
        OrderItem.objects.create(order=order, item=self.item, quantity=3)

        stripe_session_create_mock.return_value = SimpleNamespace(id="cs_order_service")

        session = services.create_order_checkout_session(order=order)

        self.assertEqual(session.id, "cs_order_service")
        configure_stripe_mock.assert_called_once_with(order.currency)

        payload = stripe_session_create_mock.call_args.kwargs
        self.assertEqual(payload["metadata"]["order_id"], str(order.id))
        self.assertEqual(payload["discounts"], [{"coupon": "coupon_existing"}])
        self.assertEqual(payload["line_items"][0]["tax_rates"], ["tax_existing"])
        self.assertEqual(payload["line_items"][0]["quantity"], 3)
        self.assertEqual(payload["line_items"][0]["price_data"]["currency"], "usd")

    @patch("apps.payments.services._configure_stripe")
    @patch("apps.payments.services.stripe.PaymentIntent.create")
    def test_create_item_payment_intent_calls_stripe_with_currency(
        self,
        stripe_payment_intent_create_mock,
        configure_stripe_mock,
    ):
        stripe_payment_intent_create_mock.return_value = SimpleNamespace(client_secret="pi_secret")

        result = services.create_item_payment_intent(
            item_id=self.item.id,
            amount=self.item.price,
            currency=self.item.currency,
        )

        self.assertEqual(result.client_secret, "pi_secret")
        configure_stripe_mock.assert_called_once_with(self.item.currency)
        stripe_payment_intent_create_mock.assert_called_once_with(
            amount=self.item.price,
            currency="usd",
            automatic_payment_methods={"enabled": True},
            metadata={"item_id": str(self.item.id)},
        )
