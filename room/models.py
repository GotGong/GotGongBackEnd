from django.db import models
from user.models import User

# Create your models here.
class Room(models.Model):
    title = models.CharField(max_length=30)
    target_time = models.DateTimeField()
    start_time = models.DateTimeField(auto_now_add=True)
    plan_half_fee = models.IntegerField()
    plan_no_fee = models.IntegerField()
    max_user_num = models.IntegerField()
    room_code = models.CharField(max_length=100)
    plan_period = models.IntegerField()
    leader_id = models.IntegerField()
    negative_percent = models.FloatField()
    user_num = models.IntegerField()


class UserRoom(models.Model):
    user = models.ForeignKey(User, related_name='user_id', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name='room_id', on_delete=models.CASCADE)
