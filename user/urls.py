from django.urls import path
from .views import signin, signup, patch_delete, check

urlpatterns = [
    path('signin/', signin),
    path('signup/', signup),
    path('', patch_delete),
    path('check/', check), # 테스트용
]
