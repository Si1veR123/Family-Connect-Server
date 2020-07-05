from django.urls import path, include
import familyconnect.urls

urlpatterns = [
    path('familyconnect/', include(familyconnect.urls)),
]
