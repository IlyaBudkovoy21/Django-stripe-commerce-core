from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from apps.catalog.models import Item
from apps.orders.models import Order

from .services import create_item_checkout_session, create_order_checkout_session


def buy_item(request, item_id: int):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    item = get_object_or_404(Item, pk=item_id)

    try:
        session = create_item_checkout_session(
            item_id=item.id,
            item_name=item.name,
            item_description=item.description,
            amount=item.price,
            currency=item.currency,
        )
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse({"id": session.id})


def buy_order(request, order_id: int):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    order = get_object_or_404(Order, pk=order_id)

    try:
        session = create_order_checkout_session(order=order)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse({"id": session.id})
