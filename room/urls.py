from django.urls import path
from .views import making_room, enter_bycode, myRoom, get_room
from .views_jjinyeok import ledaer_change, enter, patch_delete

urlpatterns = [
    path('', making_room),
    path('rooms/', get_room),
    path('list/', myRoom),
    path('enterbycode/', enter_bycode),
    path('leaderchange/', ledaer_change), 
    path('enter/', enter),
    path('', patch_delete),
]
