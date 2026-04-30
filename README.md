# Django Stripe Commerce Core

Backend service on Django for Stripe-based one-click payments for items and orders.

## Tech stack

- Python 3.12+
- Django 5.x
- Stripe Python SDK
- SQLite for local development (PostgreSQL for production)

## Quick start

1. Create virtual environment and activate it.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create env file from template:

```bash
cp .env.example .env
```

4. Run migrations and start dev server:

```bash
python manage.py migrate
python manage.py runserver
```

## Project structure

- `config/settings/` — environment-aware settings (`base`, `dev`, `prod`)
- `config/` — routes, WSGI/ASGI
- `apps/catalog/` — item catalog domain
- `apps/orders/` — order and pricing domain
- `apps/payments/` — Stripe integration and payment flows
- `apps/core/` — shared views/utilities

## Environment config

- `DJANGO_ENV=development` loads `config.settings.dev`
- `DJANGO_ENV=production` loads `config.settings.prod`
- `.env.example` contains all required runtime variables for local and production setup

## Current stage

Initial project skeleton, item payment flow, and order domain models are prepared. Feature work is split into topic branches and issue-driven commits.

## Available endpoints

- `GET /health/` — service healthcheck
- `GET /item/<id>/` — item page with Stripe checkout button
- `GET /item/<id>/intent/` — item page with Stripe Payment Intent flow
- `GET /buy/<id>/` — create Stripe Checkout session and return session id
- `GET /buy/order/<id>/` — create Stripe Checkout session for all items in order
- `GET /pay-intent/item/<id>/` — create Stripe PaymentIntent for item and return `client_secret`
- `GET /pay-intent/order/<id>/` — create Stripe PaymentIntent for order and return `client_secret`

## Order pricing extras

- `Order.discount` — optional discount model mapped to Stripe Coupon
- `Order.tax` — optional tax model mapped to Stripe TaxRate

## Multi-currency Stripe setup

- `Item.currency` supports `USD` and `EUR`
- Stripe keypairs are selected by currency via env vars:
  - `STRIPE_SECRET_KEY_USD` / `STRIPE_PUBLISHABLE_KEY_USD`
  - `STRIPE_SECRET_KEY_EUR` / `STRIPE_PUBLISHABLE_KEY_EUR`
