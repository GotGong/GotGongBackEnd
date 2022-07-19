from django.urls import path
from .views import post_patch_delete, enter_bycode, my_room, get_room
from .views_jjinyeok import leader_change, enter

urlpatterns = [
    path('', post_patch_delete),
    path('rooms/', get_room),
    path('list/', my_room),
    path('enterbycode/', enter_bycode),
    path('leaderchange/', leader_change), 
    path('enter/', enter)
]
