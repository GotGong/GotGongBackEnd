from django.urls import path
from .views import post_patch_delete, enter_by_code, my_room_list, enter, this_room_users, show_code
# from .views import get_room, leader_change 추후 추가 예정

urlpatterns = [
    path('', post_patch_delete), # 방 만들기, 방 이름 수정하기, 방 마감시 삭제
    path('myroomlist/', my_room_list), # 이미 참여한 방 리스트 조회
    path('enterbycode/', enter_by_code), # 방 참여하기 - 코드를 통해서
    path('enter/', enter), # 방 참여하기 - 이미 참여한 방으로 접속
    path('users/<int:id>/', this_room_users), # 참여한 방에서 참여자 전체 조회
    path('code/<int:id>/', show_code), # 참여코드 조회

    # path('rooms/', get_room),
    # path('leaderchange/', leader_change), 
]
