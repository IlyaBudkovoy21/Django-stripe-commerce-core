# API and Scenario Guide

## Endpoints

- `GET /health/`
- `GET /item/<id>/`
- `GET /item/<id>/intent/`
- `GET /buy/<id>/`
- `GET /buy/order/<id>/`
- `GET /pay-intent/item/<id>/`
- `GET /pay-intent/order/<id>/`

## Quick setup for test data

```bash
python manage.py migrate
python manage.py seed_demo_data
```

## cURL examples

```bash
curl -s http://localhost:8000/health/
curl -s http://localhost:8000/buy/1/
curl -s http://localhost:8000/buy/order/1/
curl -s http://localhost:8000/pay-intent/item/1/
curl -s http://localhost:8000/pay-intent/order/1/
```

## Functional test scenarios

1. Item Checkout Session:
   - open `/item/1/`
   - click Buy
   - verify redirect to Stripe Checkout

2. Item PaymentIntent:
   - open `/item/1/intent/`
   - enter Stripe test card
   - verify payment confirmation status

3. Order Checkout Session:
   - call `/buy/order/1/`
   - verify JSON contains session `id`
   - open returned checkout in browser

4. Order PaymentIntent:
   - call `/pay-intent/order/1/`
   - verify JSON contains `client_secret`

5. Discount and tax mapping:
   - create `Order` with active `Discount` and `Tax`
   - call `/buy/order/<id>/`
   - verify discount and tax are visible on Stripe side

6. Multi-currency routing:
   - ensure one `Item` in `USD` and one in `EUR`
   - call `/buy/<usd_item_id>/` and `/buy/<eur_item_id>/`
   - verify corresponding Stripe keypair is used

## Bonus coverage map

- Docker runtime: `Dockerfile`, `docker-compose.yml`
- Environment variables: `.env.example`, `config/settings/`
- Django admin: `Item`, `Order`, `Discount`, `Tax` registered
- Public deployment: `render.yaml`, `Procfile`
- Multi-item order payment: `GET /buy/order/<id>/`
- Discount and tax in checkout: implemented in Stripe session service
- Multi-currency keypairs: currency-based key resolver
- PaymentIntent flow: item and order endpoints + item intent page
