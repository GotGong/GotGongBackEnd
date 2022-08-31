from django.db import models
from django.contrib.auth.models import User

# 사용자
class User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=30, null=True) 
    email = models.CharField(max_length=50, null=True)
