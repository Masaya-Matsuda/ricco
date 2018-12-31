from django.urls import path
from trade import consumers


websocket_urlpatterns = [
    path('ws/trade/<slug:username>/', consumers.ChatConsumer),
]


