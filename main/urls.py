from django.urls import path, include
import alexa.urls

urlpatterns = [
    path('alexa/', include(alexa.urls)),
]
