from django.db import models
from room.models import Room
from user.models import User

# 계획
class Plan(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # 스터디방 FK
    content = models.TextField() # 계획 전체 요약
    success_percent = models.FloatField() # 전체 계획 달성률
    plan_start_time = models.DateField() # 계획 시작 날짜
    plan_end_time = models.DateField() # 수행 마감 날짜
    start_over_time = models.DateField() # 계획 마감 날짜 (언제까지 계획을 작성할 수 있는지)
    plan_status = models.BooleanField(default=False) # 수행 마감 지났는지 안지났는지 상태
    week = models.IntegerField() # 주차 (몇주차인지)
    dislike_check = models.IntegerField(default=0) # 싫어요 개수
    dislike_percent = models.FloatField(default=0.0) # 싫어요 퍼센트 값
    

# 세부 계획
class DetailPlan(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE) # 계획 FK
    content = models.TextField() # 세부 계획 내용
    self_check = models.BooleanField(default=False) # 세부 계획 완료 여부 (사용자가 버튼을 누르는 형식)
    dislike_check = models.IntegerField(default=0) # 싫어요 개수
    dislike_percent = models.FloatField(default=0.0) # 싫어요 퍼센트 값
    

# 사용자 계획
class UserPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 사용자 FK
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE) # 계획 FK


# 사용자 계획 싫어요
class UserPlanDislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 사용자 FK
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE) # 계획 FK
    dislike = models.BooleanField(default=False) # 싫어요 체크 여부


# 사용자 세부 수행 싫어요
class UserDetailPlanDislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 사용자 FK
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE) # 계획 FK
    dislike = models.BooleanField(default=False) # 싫어요 체크 여부
