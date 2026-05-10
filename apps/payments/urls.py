from django.urls import path

from .views import buy_item, buy_order, create_item_intent, create_order_intent


urlpatterns = [
    path("buy/<int:item_id>/", buy_item, name="buy-item"),
    path("buy/order/<int:order_id>/", buy_order, name="buy-order"),
    path("pay-intent/item/<int:item_id>/", create_item_intent, name="pay-intent-item"),
    path("pay-intent/order/<int:order_id>/", create_order_intent, name="pay-intent-order"),
]
