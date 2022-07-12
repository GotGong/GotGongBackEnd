from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=30, null=True)
    email = models.CharField(max_length=50, null=True)

    # 사용자 PK 값을 가져오기위한 함수
    def get_id(self):
        return self.id
