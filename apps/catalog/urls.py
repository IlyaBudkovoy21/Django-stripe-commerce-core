from django.urls import path

from .views import item_detail


urlpatterns = [
    path("item/<int:item_id>/", item_detail, name="item-detail"),
]
