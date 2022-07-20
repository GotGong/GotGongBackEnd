from django.db import models
from django.contrib.auth.models import User

# 사용자
class User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # 사용자 id, 패스워드
    username = models.CharField(max_length=30, null=True) # 닉네임
    email = models.CharField(max_length=50, null=True) # 이메일
