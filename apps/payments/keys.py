from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_stripe_secret_key_for_currency(currency: str) -> str:
    keypair = settings.STRIPE_KEYPAIRS.get(currency.upper(), {})
    secret_key = keypair.get("secret_key") or settings.STRIPE_SECRET_KEY
    if not secret_key:
        raise ImproperlyConfigured(f"Stripe secret key is not configured for currency {currency.upper()}")
    return secret_key


def get_stripe_publishable_key_for_currency(currency: str) -> str:
    keypair = settings.STRIPE_KEYPAIRS.get(currency.upper(), {})
    publishable_key = keypair.get("publishable_key") or settings.STRIPE_PUBLISHABLE_KEY
    if not publishable_key:
        raise ImproperlyConfigured(f"Stripe publishable key is not configured for currency {currency.upper()}")
    return publishable_key
