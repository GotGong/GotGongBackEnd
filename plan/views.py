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
from .models import Plan, UserPlan, DetailPlan, UserPlanDislike, UserDetailPlanDislike

from .serializers import PlanSerializer
from .serializers import DetailPlanSerializer

@api_view(['POST'])
def making_plan(request):
    user = get_object_or_404(User, user=request.user)
    room = Room.objects.get(id=request.data["room_id"])
    plans = Plan.objects.filter(room=room)
    userplan_list = []
    for plan in plans:
        if UserPlan.objects.filter(user=user, plan=plan).exists():
            userplan = UserPlan.objects.get(user=user, plan=plan)
            userplan_list.append(userplan)

    if userplan_list:
        last_plan = userplan_list[0].plan
        plan = Plan.objects.create(
            room=room,
            plan_start_time=last_plan.plan_end_time,
            plan_end_time=last_plan.plan_end_time+datetime.timedelta(days=7),
            start_over_time=last_plan.plan_end_time+datetime.timedelta(days=3),
            week=last_plan.week + 1,
            content=request.data['content']
        )
        last_plan.plan_status=False
        last_plan.save()
    else:
        plan = Plan.objects.create(
            room=room,
            plan_start_time=room.start_date,
            plan_end_time=room.start_date + datetime.timedelta(days=7),
            start_over_time=room.start_date + +datetime.timedelta(days=3),
            content = request.data['content']
        )
    plan.save()
    userplan = UserPlan.objects.create(user = user, plan = plan)
    userplan.save()

    for i in range(request.data['detail_num']):
        detail_plan = DetailPlan.objects.create(
            plan = plan,
            content = request.data['detail_content'][i]
        )
        detail_plan.save()

    return Response({"plan_id": plan.id}, status=status.HTTP_200_OK)


@api_view(['GET'])
def myplan_content_endtime(request):
    user = get_object_or_404(User, user=request.user)
    room = Room.objects.get(id=request.data["room_id"])
    plans = Plan.objects.filter(room=room, plan_status=True)
    userplan_list = []
    for plan in plans:
        if UserPlan.objects.filter(user=user, plan=plan).exists():
            userplan = UserPlan.objects.get(user=user, plan=plan)
            userplan_list.append(userplan)
    if userplan_list:
        plan_dday = userplan.plan.plan_end_time-datetime.date.today()
        study_dday = room.target_date-datetime.date.today()
        return Response({'content': userplan.plan.content, 'plan_dday': plan_dday.days, 'study_dday': study_dday.days}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_204_NO_CONTENT)


def show_plans(request):
    user = get_object_or_404(User, user=request.user)
    room = Room.objects.get(id=request.data["room_id"])
    plans = Plan.objects.filter(room=room)
    plan_list = []
    for plan in plans:
        if UserPlan.objects.filter(user=user, plan=plan).exists() == False:
            plans = plans.exclude(id=plan.id)
        else:
            plan_list.append(plan)
    plan_info = plans.values('id','content','plan_status','week','dislike_check')
    for i in range(len(plan_info)):
        detail_list = DetailPlan.objects.filter(plan=plan_list[i]).values_list('content', flat=True)
        plan_info[i]['detail_plans'] = detail_list
    return plan_info


@api_view(['GET'])
def user_plans(request):
    plan_info = show_plans(request)
    return Response(plan_info, status=status.HTTP_200_OK)


@api_view(['GET'])
def my_detail_plans(request):
    plan_info = show_plans(request)
    user = get_object_or_404(User, user=request.user)
    room = Room.objects.get(id=request.data["room_id"])
    plans = Plan.objects.filter(room=room)
    plan_list = []
    for plan in plans:
        if UserPlan.objects.filter(user=user, plan=plan).exists():
            plan_list.append(plan)
    for i in range(len(plan_info)):
        del plan_info[i]['detail_plans']
        detail_dic = DetailPlan.objects.filter(plan=plan_list[i]).values('id', 'dislike_check', 'content')
        plan_info[i]['detail_plan'] = detail_dic
        del plan_info[i]['dislike_check']

    return Response(plan_info, status=status.HTTP_200_OK)


@api_view(['POST'])
def plan_dislike(request):
    user = get_object_or_404(User, user=request.user)
    plan = Plan.objects.get(id=request.data['plan_id'])
    if UserPlanDislike.objects.filter(user=user, plan=plan).exists():
        return Response({'error_code': 'USER_ALREADY_PUSH_DISLIKE'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        plan.dislike_check += 1
        plan.save()
        plan.dislike_percent = plan.dislike_check/plan.room.user_num
        plan.save()
        userplandislike = UserPlanDislike.objects.create(user=user, plan=plan, dislike=True)
        userplandislike.save()
        return Response({'check_num': plan.dislike_check, 'dislike_percent': plan.dislike_percent}, status=status.HTTP_200_OK)


@api_view(['GET'])
def ranking(request):
    room = Room.objects.get(id=request.data['room_id'])
    userrooms = UserRoom.objects.filter(room=room)
    percent_sum = {}
    for userroom in userrooms:
        plan_percent = 0
        plan_num = 0
        userplans = UserPlan.objects.filter(user=userroom.user)
        for userplan in userplans:
            if (userplan.plan.room.id == int(request.data['room_id'])):
                done_plan_num = 0
                detail_plans = DetailPlan.objects.filter(plan=userplan.plan)
                plan_num += 1
                for detail_plan in detail_plans:
                    if detail_plan.self_check == True:
                        done_plan_num += 1
                plan_percent += done_plan_num/len(detail_plans)
        percent_sum[userroom.user.username] = round(plan_percent*(1/plan_num), 2)
        userroom.percent_sum = round(plan_percent*(1/plan_num), 2)
        userroom.save()
    percent_sum=dict(sorted(percent_sum.items(), key=lambda item: item[1], reverse=True))
    return Response(percent_sum, status=status.HTTP_200_OK)


@api_view(['GET'])
def refund_calculation(request):
    room = Room.objects.get(id=request.data['room_id'])
    userrooms = UserRoom.objects.filter(room=room)
    percent_dic = {}
    refund_list=[]
    for userroom in userrooms:
        percent_dic[userroom.user.username] = userroom.percent_sum
    percent_dic = dict(sorted(percent_dic.items(), key=lambda item: item[1], reverse=True))

    usernames = list(percent_dic.keys())
    # 1번룰 / 1등 200%, 2~5등 100%, 6등 0%
    if int(request.data['rule']) == 0:
        for i in range(len(usernames)):
            if i == 0:
                percent_dic[usernames[0]] = 2*20000
            elif i == (len(usernames) -1):
                percent_dic[usernames[i]] = 0
            else:
                percent_dic[usernames[i]] = 20000
    # 2번 룰
    # 3인 기준 / 1등 160%. 2등 80% 3등 60%
    # 4인 기준 / 1등 180%. 2~3등 80%. 4등 60%
    # 5인 기준 / 1등 200%. 2~4등 80%. 5등 60%
    # 6인 기준 / 1등 180%. 2~5등 90%. 6등 60%
    else:
        if room.user_num == 3:
            percent_dic[usernames[0]] = round(1.6*20000)
            percent_dic[usernames[1]] = round(0.8*20000)
            percent_dic[usernames[2]] = round(0.6*20000)
        elif room.user_num == 4 or room.user_num == 5:
            for i in range(len(usernames)):
                if i == 0:
                    if room.user_num == 4:
                        percent_dic[usernames[0]] = round(1.8*20000)
                    else:
                        percent_dic[usernames[i]] = 2*20000
                elif i == (len(usernames)-1):
                    percent_dic[usernames[i]] = round(0.6*20000)
                else:
                    percent_dic[usernames[i]] = round(0.8*20000)
        else:
            for i in range(len(usernames)):
                if i == 0:
                    percent_dic[usernames[0]] = round(1.8*20000)
                elif i == (len(usernames)-1):
                    percent_dic[usernames[i]] = round(0.6*20000)
                else:
                    percent_dic[usernames[i]] = round(0.9*20000)        
    return Response(percent_dic, status=status.HTTP_200_OK)


@api_view(['POST'])
def dplan_dislike_and_check(request):
    user = get_object_or_404(User, user=request.user)
    dplan = DetailPlan.objects.get(id=request.data['detailplan_id'])
    plan = request.data['plan']
    if UserDetailPlanDislike.objects.filter(user=user, plan=plan).exists():
        return Response({'error_code': 'USER_ALREADY_PUSH_DISLIKE'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        if request.data['self_check'] == True:
            dplan.self_check = True
        dplan.dislike_check += 1
        dplan.save()
        dplan.dislike_percent = dplan.dislike_check/dplan.plan.room.user_num
        dplan.save()
        dplandislike = UserDetailPlanDislike.objects.create(user=user, plan=plan, dislike=True)
        dplandislike.save()
        return Response({'check_num': dplan.dislike_check, 'dislike_percent': dplan.dislike_percent}, status=status.HTTP_200_OK)



@api_view(['PATCH', 'DELETE'])
def plan_patch_delete(request):
    user = get_object_or_404(User, user=request.user)
    d_plan = DetailPlan.objects.get(id=request.data['detail_plan_id'])
    plan = Plan.objects.get(id=request.data['plan_id'])
    if d_plan.exists() and plan.exists():
        pass
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PATCH':
        plan_tochange = request.data['plan_tochange']
        serializer = PlanSerializer(plan.first(), data=request.data['plan_tochange'], partial=True)
        serializer_1 = DetailPlanSerializer(d_plan.first(), data=request.data['dplan_tochange'], partial=True)
        if serializer.is_valid():
            serializer.save()
            serializer_1.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        d_plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
