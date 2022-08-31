from django.urls import path
from .views import *
# from .views import check

urlpatterns = [
    path('signin/', signin), # 로그인
    path('signup/', signup), # 회원가입
    path('', get_delete), # 사용자 이름변경, 사용자 탈퇴
    path('id/', patch_id),
    path('password/', patch_password),
    path('username/', patch_username),
    path('duplicationcheck/', duplicationcheck), # 아이디 중복체크
    # path('check/', check), # 테스트용
]
