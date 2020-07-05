from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path('familyconnect/ws/', consumers.FamilyConnectConsumer),
]
