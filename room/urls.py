from django.urls import path
from .views import making_room, enter_bycode, myRoom, get_room

urlpatterns = [
    path('', making_room),
    path('rooms/', get_room),
    path('list/', myRoom),
    path('enterbycode/', enter_bycode),
]
