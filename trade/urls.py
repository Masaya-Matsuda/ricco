from trade import views
from django.urls import path
from django.conf.urls import url, include


app_name = "trade"

urlpatterns = [
    path("", views.trade, name="trade"),
]

