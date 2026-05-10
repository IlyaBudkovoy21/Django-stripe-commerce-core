from django.urls import path

from .views import item_detail, item_payment_intent_page


urlpatterns = [
    path("item/<int:item_id>/", item_detail, name="item-detail"),
    path("item/<int:item_id>/intent/", item_payment_intent_page, name="item-intent-page"),
]
