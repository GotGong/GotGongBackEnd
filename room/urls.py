from django.urls import path
from .views import post_patch_delete, enter_by_code, my_room_list, enter
# from .views import get_room, leader_change

urlpatterns = [
    path('', post_patch_delete),
    path('myroomlist/', my_room_list),
    path('enterbycode/', enter_by_code),
    path('enter/', enter)
    # path('rooms/', get_room),
    # path('leaderchange/', leader_change), 
]
