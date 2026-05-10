# Deployment Runbook

## Goal

Deploy a publicly accessible instance that reviewers can test in 5-10 minutes, including `/admin/` access.

## Recommended platform

- Render (blueprint file `render.yaml` is already included)

## Pre-deploy checklist

- Repository is up to date on `develop` or `main`
- Stripe test keys are ready for both currencies:
  - `STRIPE_SECRET_KEY_USD`, `STRIPE_PUBLISHABLE_KEY_USD`
  - `STRIPE_SECRET_KEY_EUR`, `STRIPE_PUBLISHABLE_KEY_EUR`
- Admin credentials decided:
  - `DJANGO_SUPERUSER_USERNAME`
  - `DJANGO_SUPERUSER_EMAIL`
  - `DJANGO_SUPERUSER_PASSWORD`

## Render deployment (blueprint)

1. In Render, choose "New" -> "Blueprint".
2. Connect this repository and select `render.yaml`.
3. Fill required env vars marked `sync: false`:
   - Stripe keys
   - Superuser credentials
4. Deploy.

## Post-deploy smoke checks

- Open `https://<your-domain>/health/` and confirm `{"status":"ok"}`
- Open `https://<your-domain>/admin/` and login with provided admin credentials
- Run seed command from Render shell:

```bash
python manage.py seed_demo_data
```

- Open one item page and verify Checkout Session flow starts
- Open one intent page and verify PaymentIntent flow initializes

## Reviewer handoff template

- Public URL: `https://<your-domain>/`
- Admin URL: `https://<your-domain>/admin/`
- Admin login: `<username>` / `<password>`
- Demo steps:
  1. Open `/admin/`, verify items and orders
  2. Open `/item/1/`, click Buy (Checkout Session)
  3. Open `/item/1/intent/`, test PaymentIntent form
  4. Call `/buy/order/1/` and `/pay-intent/order/1/`
