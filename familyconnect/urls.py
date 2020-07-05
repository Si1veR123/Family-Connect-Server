from django.urls import path
from . views import *

urlpatterns = [
    path('alexa/', alexa),
    path('idcheck/<str:id>', id_check)
]
