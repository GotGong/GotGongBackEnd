from django.db import models
from room.models import Room
from user.models import User
# Create your models here.

class Plan(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    end_time = models.DateTimeField() 
    revision_request = models.IntegerField()
    plan_status = models.BooleanField(default=True)
    week = models.IntegerField()
    plan_start_time = models.DateTimeField()
    

class Detail_Plan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    content = models.CharField(max_length=50)
    peer_negative_review = models.IntegerField()    # defalut = 0
    self_check = models.BooleanField(default=False)
    
