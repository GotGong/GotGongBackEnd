from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import datetime

from user.models import User
from room.models import Room, UserRoom
from .serializers import PlanSerializer, DetailPlanSerializer
from .models import Plan, UserPlan, DetailPlan, UserPlanDislike, UserDetailPlanDislike

@api_view(['POST'])
def making_plan(request):
    """사용자가 현재 들어와 있는 방의 id와 content, detail_num, detail_content들을 입력받아 해당 주차의 새로운 Plan과 DetailPlan을 만들 수 있도록 하는 함수
    
    :param string user: user token
    :param int room: room_id
    :param string content: plan_content
    :param int detail_num: detail_plan_num
    :param list detail_content: detail_plan_content
    
    :returns int: plan_id
    """
    user = get_object_or_404(User, user=request.user)
    room = Room.objects.get(id=request.data["room_id"])
    plans = Plan.objects.filter(room=room)
    userplan_list = []
    for plan in plans:
        if UserPlan.objects.filter(user=user, plan=plan).exists():
            userplan = UserPlan.objects.get(user=user, plan=plan)
            userplan_list.append(userplan)

    if userplan_list:
        last_plan = userplan_list[-1].plan
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
            room = room,
            plan_start_time=room.start_date,
            plan_end_time=room.start_date + datetime.timedelta(days=7),
            start_over_time=room.start_date + datetime.timedelta(days=3),
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
def myplan_content_endtime(request, id):
    """사용자가 현재 들어와 있는 방의 id를 입력받아 현재 진행 중인 계획의 마감기한과 스터디 진행 정도를 알려주는 함수
    
    :param string user: user token
    :param int room: room_id
    
    :returns string content: 사용자의 진행 중인 계획 content
    :returns int plan_dday: 현재 진행 중인 계획의 마감기한
    :returns int study_days: 스터디 진행 정도
    """
    user = get_object_or_404(User, user=request.user)
    room = get_object_or_404(Room, id=id)
    plans = Plan.objects.filter(room=room, plan_status=True)
    userplan_list = []
    for plan in plans:
        if UserPlan.objects.filter(user=user, plan=plan).exists():
            userplan = UserPlan.objects.get(user=user, plan=plan)
            userplan_list.append(userplan)
    if userplan_list:
        plan_dday = userplan.plan.plan_end_time-datetime.date.today()
        study_dday = userplan.plan.room.target_date-datetime.date.today()
        return Response({'content': userplan.plan.content, 'plan_dday': plan_dday.days, 'study_dday': study_dday.days}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_204_NO_CONTENT)


def show_plans(request,id):
    user = get_object_or_404(User, user=request.user)
    room = get_object_or_404(Room, id=id)
    plans = Plan.objects.filter(room=room)
    plan_list = []
    for plan in plans:
        if UserPlan.objects.filter(user=user, plan=plan).exists() == False:
            plans = plans.exclude(id=plan.id)
        else:
            plan_list.append(plan)
    plan_info = plans.values('id','content','plan_status','week','dislike_check')
    for i in range(len(plan_info)):
        detail_dic = DetailPlan.objects.filter(plan=plan_list[i]).values('content', 'self_check')
        plan_info[i]['detail_plans'] = detail_dic
    return plan_info


@api_view(['GET'])
def other_user_plans(request, user_id, room_id):
    user = get_object_or_404(User, id=user_id)
    room = get_object_or_404(Room, id=room_id)
    plans = Plan.objects.filter(room=room)
    plan_list = []    
    for plan in plans:
        if UserPlan.objects.filter(user=user, plan=plan).exists() == False:
            plans = plans.exclude(id=plan.id)
        else:
            plan_list.append(plan)
    plan_info = plans.values('id','content','plan_status','week','dislike_check')
    for i in range(len(plan_info)):
        detail_dic = DetailPlan.objects.filter(plan=plan_list[i]).values('content', 'self_check')
        plan_info[i]['detail_plans'] = detail_dic
    entire_week = room.target_date - room.start_date
    username = user.username
    return Response({"plan_info":plan_info, "entire_week": entire_week.days, "username": username}, status=status.HTTP_200_OK)
    
    
@api_view(['GET'])
def user_plans(request,id):
    """사용자가 현재 들어와 있는 방의 id를 입력받아 현재 방에서 사용자의 모든 계획의 정보를 불러오는 함수
    
    :param string user: user token
    :param int room: room_id
    
    :returns int id: plan_id
    :returns string content: plan_content
    :returns boolean plan_status: plan_status
    :returns int week: plan_week
    :returns int dislike_check: plan_dislike_check
    :returns list detail_plans: detail_plan_contents
    """
    plan_info = show_plans(request,id)
    room = get_object_or_404(Room, id=id)
    entire_week = room.target_date - room.start_date
    return Response({"plan_info":plan_info, "entire_week": entire_week.days}, status=status.HTTP_200_OK)


@api_view(['GET'])
def my_detail_plans(request,id):
    """사용자가 현재 들어와 있는 방의 id를 입력받아 현재 방에서 사용자의 detail_plan에 대한 세부 정보를 불러오는 함수
    
    :param string user: user token
    :param int room: room_id
    
    :returns int id: plan_id
    :returns string content: plan_content
    :returns boolean plan_status: plan_status
    :returns int week: plan_week
    :returns list detail_plan: detail_plan_id, detail_plan_dislike_check, detail_plan_content
    """
    plan_info = show_plans(request, id)
    user = get_object_or_404(User, user=request.user)
    room = get_object_or_404(Room, id=id)
    plans = Plan.objects.filter(room=room)
    plan_list = []
    for plan in plans:
        if UserPlan.objects.filter(user=user, plan=plan).exists():
            plan_list.append(plan)
    for i in range(len(plan_info)):
        del plan_info[i]['detail_plans']
        detail_dic = DetailPlan.objects.filter(plan=plan_list[i]).values('id', 'dislike_check', 'content', 'self_check')
        plan_info[i]['detail_plan'] = detail_dic
        del plan_info[i]['dislike_check']

    entire_week = room.target_date-room.start_date
    return Response({"plan_info":plan_info, "entire_week": entire_week.days}, status=status.HTTP_200_OK)


@api_view(['POST'])
def plan_dislike(request):
    """다른 사용자의 계획 id를 입력받아 사용자가 그 계획의 수행을 평가하는 함수 
    
    :param string user: user token
    :param int plan: plan_id
    
    :returns int check_num: plan_dislike_check
    :returns float dislike_percent: plan_dislike_percent
    """
    user = get_object_or_404(User, user=request.user)
    plan = Plan.objects.get(id=request.data['plan_id'])
    if UserPlanDislike.objects.filter(user=user, plan=plan).exists():
        return Response({'error_code': 'USER_ALREADY_PUSH_DISLIKE'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        plan.dislike_check += 1
        plan.dislike_percent = plan.dislike_check/plan.room.user_num
        plan.save()
        userplandislike = UserPlanDislike.objects.create(user=user, plan=plan, dislike=True)
        userplandislike.save()
        return Response({'check_num': plan.dislike_check, 'dislike_percent': plan.dislike_percent}, status=status.HTTP_200_OK)


@api_view(['GET'])
def ranking(request, id):
    """방 id를 입력받아 사용자들의 percent_sum을 계산하고 높은 순서대로 정렬하여 딕셔녀리 형태로 내보내는 함수
    
    :params int room: room_id
    
    :returns json percent sum: {username: percent_sum}
    """
    room = get_object_or_404(Room, id=id)
    userrooms = UserRoom.objects.filter(room=room)
    percent_sum = {}
    for userroom in userrooms:
        plan_percent = 0
        plan_num = 0
        userplans = UserPlan.objects.filter(user=userroom.user)
        for userplan in userplans:
            if userplan.plan.room.id == id:
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
def refund_calculation(request, id):
    """방 id를 입력받아 rule_num의 규칙에 따라서 환급금을 계산하고 높은 순서대로 정렬하여 딕셔녀리 형태로 내보내는 함수
    
    :params int room: room_id
    
    :returns json percent_dic: {username: refund}
    """
    room = Room.objects.get(id=id)
    userrooms = UserRoom.objects.filter(room=room)
    percent_dic = {}
    for userroom in userrooms:
        percent_dic[userroom.user.username] = userroom.percent_sum
    percent_dic = dict(sorted(percent_dic.items(), key=lambda item: item[1], reverse=True))

    usernames = list(percent_dic.keys())
    # 1번룰 / 1등 200%, 2~5등 100%, 6등 0%
    if room.rule_num == 0:
        for i in range(len(usernames)):
            if i == 0:
                percent_dic[usernames[0]] = 2*room.entry_fee
            elif i == (len(usernames) -1):
                percent_dic[usernames[i]] = 0
            else:
                percent_dic[usernames[i]] = room.entry_fee
    # 2번 룰
    # 3인 기준 / 1등 160%. 2등 80% 3등 60%
    # 4인 기준 / 1등 180%. 2~3등 80%. 4등 60%
    # 5인 기준 / 1등 200%. 2~4등 80%. 5등 60%
    # 6인 기준 / 1등 180%. 2~5등 90%. 6등 60%
    else:
        if room.user_num == 3:
            percent_dic[usernames[0]] = round(1.6*room.entry_fee)
            percent_dic[usernames[1]] = round(0.8*room.entry_fee)
            percent_dic[usernames[2]] = round(0.6*room.entry_fee)
        elif room.user_num == 4 or room.user_num == 5:
            for i in range(len(usernames)):
                if i == 0:
                    if room.user_num == 4:
                        percent_dic[usernames[0]] = round(1.8*room.entry_fee)
                    else:
                        percent_dic[usernames[i]] = 2*room.entry_fee
                elif i == (len(usernames)-1):
                    percent_dic[usernames[i]] = round(0.6*room.entry_fee)
                else:
                    percent_dic[usernames[i]] = round(0.8*room.entry_fee)
        else:
            for i in range(len(usernames)):
                if i == 0:
                    percent_dic[usernames[0]] = round(1.8*room.entry_fee)
                elif i == (len(usernames)-1):
                    percent_dic[usernames[i]] = round(0.6*room.entry_fee)
                else:
                    percent_dic[usernames[i]] = round(0.9*room.entry_fee)        
    return Response(percent_dic, status=status.HTTP_200_OK)


@api_view(['POST'])
def dplan_dislike_and_check(request):
    """다른 사용자의 detail_plan id를 입력받아 사용자가 그 detail_plan이나 자신의 수행을 평가하는 함수
    
    :params string user: user token
    :params int dplan: detailplan_id
    :params boolean self_check: detailplan_self_check
    
    :returns int check_num: detailplan_dislike_check
    :returns float dislike_percent: detailplan_dislike_percent
    """
    user = get_object_or_404(User, user=request.user)
    dplan = DetailPlan.objects.get(id=request.data['detailplan_id'])
    if UserDetailPlanDislike.objects.filter(user=user, detail_plan=dplan).exists():
        return Response({'error_code': 'USER_ALREADY_PUSH_DISLIKE'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        if request.data['self_check'] == True:
            dplan.self_check = True
        dplan.dislike_check += 1
        dplan.dislike_percent = dplan.dislike_check/dplan.plan.room.user_num
        dplan.save()
        dplandislike = UserDetailPlanDislike.objects.create(user=user, detail_plan=dplan, dislike=True)
        dplandislike.save()
        return Response({'check_num': dplan.dislike_check, 'dislike_percent': dplan.dislike_percent}, status=status.HTTP_200_OK)



@api_view(['PATCH', 'DELETE'])
def plan_patch_delete(request):
    """사용자의 detail_plan을 수정하거나 제거하는 함수
    
    :params string user: user token
    :params int d_plan: detail_plan_id
    :params int plan: plan_id
    
    :returns None:
    """
    user = get_object_or_404(User, user=request.user)
    d_plan = DetailPlan.objects.get(id=request.data['detail_plan_id'])
    plan = Plan.objects.get(id=request.data['plan_id'])
    if d_plan.exists() and plan.exists():
        pass
    elif UserPlan.objects.get(plan=plan,user=user).exists():
        pass
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PATCH':
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
