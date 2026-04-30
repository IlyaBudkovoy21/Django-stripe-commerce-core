from django.conf import settings
from django.shortcuts import get_object_or_404, render

from .models import Item


def item_detail(request, item_id: int):
    item = get_object_or_404(Item, pk=item_id)
    context = {
        "item": item,
        "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, "catalog/item_detail.html", context)
