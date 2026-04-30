from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ImproperlyConfigured

from apps.payments.keys import get_stripe_publishable_key_for_currency

from .models import Item


def item_detail(request, item_id: int):
    item = get_object_or_404(Item, pk=item_id)
    try:
        stripe_publishable_key = get_stripe_publishable_key_for_currency(item.currency)
    except ImproperlyConfigured:
        stripe_publishable_key = ""

    context = {
        "item": item,
        "stripe_publishable_key": stripe_publishable_key,
    }
    return render(request, "catalog/item_detail.html", context)
