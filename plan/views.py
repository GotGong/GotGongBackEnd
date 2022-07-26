from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from rest_framework import status
from django.utils import timezone
import datetime
from django.http import HttpResponse
from django.core import serializers

from user.models import User
from . import models
from room.models import Room, UserRoom
from .models import Plan, UserPlan, DetailPlan

from .serializers import PlanSerializer
from .serializers import DetailPlanSerializer

@api_view(['POST'])
def making_plan(request):
    user = get_object_or_404(User, user=request.user)
    room = Room.objects.get(id=request.data["room_id"])

    if Plan.objects.filter(room=room).exists():
        last_plan = Plan.objects.filter(room=room).last()
        plan = Plan.objects.create(
            room=room,
            plan_start_time=last_plan.plan_end_time,
            plan_end_time=last_plan.plan_end_time+datetime.timedelta(days=7),
            start_over_time=last_plan.plan_end_time+datetime.timedelta(days=3),
            week=last_plan.week + 1,
            content=request.data['content'],
        )
        last_plan.plan_status=False
    else:
        plan = Plan.objects.create(
            room=room,
            plan_start_time=room.start_date,
            plan_end_time=room.start_date + datetime.timedelta(days=7),
            start_over_time=room.start_date + +datetime.timedelta(days=3),
            content = request.data['content']
        )
    plan.save()
    last_plan.save()
    userplan = models.UserPlan(user = user, plan = plan)
    userplan.save()
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
def myplan_content_endtime(request):
    user = get_object_or_404(User, user=request.user)
    room = Room.objects.get(id=request.data["room_id"])
    plan = Plan.objects.get(room=room, plan_status=True)
    userplan = UserPlan.objects.get(user=user, plan=plan)
    plan_dday = plan.plan_end_time-datetime.date.today()
    study_dday = room.target_date-datetime.date.today()
    return Response({'content': userplan.plan.content, 'plan_dday': plan_dday.days, 'study_dday': study_dday.days}, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def user_plans(request):
    user = get_object_or_404(User, user=request.user)
    room = Room.objects.get(id=request.data["room_id"])
    plans = Plan.objects.filter(room=room)
    user_plans_list_1 = []
    for plan in plans:
        userplan = UserPlan.objects.filter(user=user, plan=plan)
        plan = Plan.objects.filter(id=userplan.plan.id).values('content','plan_status','week','dislike_check')
        user_plans_list_1.append(plan)
    return Response(user_plans_list_1, status=status.HTTP_200_OK)

# @api_view(['POST'])
# def making_detail_plan(request):
#     user = get_object_or_404(User, user=request.user)
#     plan = Plan.objects.get(id=request.data['plan_id'])
#     detail_plan = DetailPlan.objects.create(
#         user=user,
#         plan=plan,
#         content=request.data['content'],
#         peer_negative_review=0
#     )
#     detail_plan.save()
#     return Response(status=status.HTTP_200_OK)


# @api_view(['GET'])
# def all_detail_plan(request):
#     user = get_object_or_404(User, user=request.user)
#     plan = Plan.objects.get(id=request.data['plan_id'])
#     detail_plan = DetailPlan.objects.filter(user=user, plan=plan)
#     d_plan_list = serializers.serialize('json', detail_plan)
#     return HttpResponse(d_plan_list, content_type="text/json-coomment-filtered")


# @api_view(['GET'])
# def all_plan(request):
#     user = get_object_or_404(User, user=request.user)
#     room = Room.objects.get(id=request.data['room_id'])
#     plan = Plan.objects.filter(room=room)
#     if UserRoom.objects.filter(user=user, room=room).exists():
#         plan_list = serializers.serialize('json', plan)
#         return HttpResponse(plan_list, content_type="text/json-coomment-filtered")
#     else:
#         return Response(status=status.HTTP_404_NOT_FOUND)


# @api_view(['PATCH', 'DELETE'])
# def plan_patch_delete(request):
#     user = get_object_or_404(User, user=request.user)
#     d_plan = DetailPlan.objects.filter(id=request.data['detail_plan_id'], user=user)
#     if d_plan.exists():
#         pass
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     if request.method == 'PATCH':
#         serializer = DetailPlanSerializer(d_plan.first(), data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     elif request.method == 'DELETE':
#         d_plan.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)