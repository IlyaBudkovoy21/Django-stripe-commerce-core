from django.urls import path

from .views import buy_item, buy_order


urlpatterns = [
    path("buy/<int:item_id>/", buy_item, name="buy-item"),
    path("buy/order/<int:order_id>/", buy_order, name="buy-order"),
]
