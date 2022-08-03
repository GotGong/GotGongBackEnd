from django.db import models
from user.models import User

# 스터디방
class Room(models.Model):
    title = models.CharField(max_length=30) # 방 이름
    target_date = models.DateField() # 스터디방 일정 (스터디방 마감 날짜)
    max_user_num = models.IntegerField() # 스터디방 최대 인원
    rule_num = models.IntegerField() # 스터디방 룰 번호 (0 or 1)
    user_num = models.IntegerField() # 스터디방 현재 인원
    start_date = models.DateField(auto_now_add=True) # 스터디방 시작 날짜
    leader_id = models.IntegerField() # 방장 ID
    room_code = models.CharField(max_length=15) # 방코드(입장용)
    entry_fee = models.IntegerField() # 참가비


# 사용자 스터디방
class UserRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 사용자 FK
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # 스터디방 FK
    percent_sum = models.FloatField() # 지금까지 한 공부들에 대한 퍼센트 값
    refund = models.IntegerField() # 환급금
