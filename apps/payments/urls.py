from django.urls import path

from .views import buy_item


urlpatterns = [
    path("buy/<int:item_id>/", buy_item, name="buy-item"),
]
