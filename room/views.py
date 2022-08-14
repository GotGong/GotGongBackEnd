from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from user.models import User
from . import models
from .models import Room
from .models import UserRoom
from .serializers import RoomSerializer
from user.serializers import UserSerializer

import datetime

import uuid
import base64
import codecs

# WUJtQT09와 같은 형태로 랜덤 코드 생성 함수
def generate_random_slug_code(length=15):  # length는 1-32사이에 존재해야 함.
    return base64.urlsafe_b64encode(       # url에서도 랜덤 코드를 사용가능하게 하기 위한 함수
        codecs.encode(uuid.uuid4().bytes, 'base64').rstrip() # base64로 인코딩
    ).decode()[:length] # 바이트스트링 타입을 문자열로 활용하기 위한 코드


# 방 만들기, 방 이름 수정하기, 방 마감시 삭제
@api_view(['POST','PATCH', 'DELETE'])
def post_patch_delete(request):
    # 방 만들기
    if request.method == 'POST':
        user = get_object_or_404(User, user=request.user)
        # [FIX]: code 중복 생성 방지
        while True:
            room_code = generate_random_slug_code()
            if Room.objects.filter(room_code=room_code).exists():
                continue
            else:
                break
        room = Room.objects.create(
            title = request.data['title'], 
            target_date = request.data['target_date'], 
            max_user_num = request.data['max_user_num'], 
            rule_num = request.data['rule_num'], 
            user_num = 1, 
            leader_id = user.id,
            room_code = room_code
        )
        room.save()
        userroom = models.UserRoom(user = user, room = room, percent_sum = 0.0, refund = 0)
        userroom.save()
        return Response({'room_id': room.id, 'room_code': room_code}, status=status.HTTP_200_OK)

    # 방 이름, 인원 수정하기
    elif request.method == 'PATCH':
        user, room_id, title_to_change, num_to_change = get_object_or_404(User, user=request.user), request.data['room_id'], request.data['title'], request.data['user_num']
        room = get_object_or_404(Room, id=room_id)
        if user.id == room.leader_id:
            room.title = title_to_change
            room.user_num = num_to_change
            room.save()
            return Response({'room_id': room.id}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 방 마감시 삭제
    elif request.method == 'DELETE':
        rooms = Room.objects.all()
        now_date_time = timezone.now()
        for room in rooms:
            if room.target_time < now_date_time:
                room.delete()
        return Response(status=status.HTTP_200_OK)


# 이미 참여한 방 리스트 조회
@api_view(['GET'])
def my_room_list(request):
    user = get_object_or_404(User, user=request.user)
    userrooms = UserRoom.objects.filter(user=user)
    room_num, response_rooms = 0, []
    for userroom in userrooms:
        room = userroom.room
        room = Room.objects.get(id=room.id)
        room_serializer = RoomSerializer(room)
        room_serializer_data = room_serializer.data
        response_rooms.append(room_serializer_data)
    room_num = len(response_rooms)
    return Response({'room_count': room_num, 'my_room_list': response_rooms}, status=status.HTTP_200_OK)


# 참여한 방에서 참여자 전체 조회
@api_view(['GET'])
def this_room_users(request, id):
    room = get_object_or_404(Room, id=id)
    userrooms = UserRoom.objects.filter(room=room)
    user_count, user_list = 0, []
    for userroom in userrooms:
        user = userroom.user
        user_serializer = UserSerializer(user)
        user_serializer_data = user_serializer.data
        user_list.append(user_serializer_data)
    user_count = len(user_list)
    return Response({'room_user_count': user_count, 'room_users_list': user_list}, status=status.HTTP_200_OK)


# 참여코드 조회
@api_view(['GET'])
def show_code(request, id):
    user = get_object_or_404(User, user=request.user)
    room = get_object_or_404(Room, id=id)
    if UserRoom.objects.filter(user=user, room=room).exists():
        return Response(room.room_code, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


# 방 참여하기 - 코드를 통해서
@api_view(['POST'])
def enter_by_code (request):
    user, room_code = get_object_or_404(User, user=request.user), request.data['room_code']
    if Room.objects.filter(room_code=room_code).exists():
        room = Room.objects.get(room_code=room_code)
        if UserRoom.objects.filter(user=user, room=room).exists():
            return Response({'error_code': 'USER_ALREADY_JOIN_ROOM'}, status=status.HTTP_400_BAD_REQUEST)
        # [FIX]: user_num이 max_user_num보다 많아지는 것 방지
        elif room.user_num == room.max_user_num:
            return Response({'error_code': 'ROOM_IS_FULL'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            room.user_num += 1
            room.save()
            userroom = models.UserRoom(user=user, room=room, percent_sum=0.0, refund = 0)
            userroom.save()
            return Response({'room_id': room.id}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


# 방 참여하기 - 이미 참여한 방으로 접속
@api_view(['POST'])
def enter(request):
    user, room_id = get_object_or_404(User, user=request.user), request.data['room_id']
    room = get_object_or_404(Room, id=room_id)
    user_room = get_object_or_404(UserRoom, user=user, room=room)
    if user_room:
        return Response({'room_id': room_id} ,status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 룰 변경하기
@api_view(['PATCH'])
def change_rule(request):
    """This function is changing rule in the room.
    
    Params
    ------
    user : by token
    room_id : the room id
    rule_num : rule number to change

    Return
    ------
    SUCCESS -> HTTP_200_OK : room_id : the room id
    FAIL -> HTTP_400_BAD_REQUEST
    """

    # user, room_id, rule_num_to_chage : request parmas
    user, room_id, rule_num_to_change = get_object_or_404(User, user=request.user), request.data['room_id'], request.data['rule_num']
    room = get_object_or_404(Room, id=room_id)
    # only leader can change the rule
    if user.id == room.leader_id:
        # the room's rule changed
        room.rule_num = rule_num_to_change
        room.save()
        return Response({'room_id': room.id}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


# 일정 변경하기 (주차 변경하기)
@api_view(['PATCH'])
def change_target_date(request):
    """This function is changing schedule by week in the room

    Params
    ------
    user : by token
    room_id : the room id
    target_date_week : week to changing the target date

    Return
    ------
    SUCCESS -> HTTP_200_OK : room_id : the room id
    FAIL -> HTTP_400_BAD_REQUEST
    """

    # user, room_id, target_date_week_to_chage : request parmas
    user, room_id, target_date_week_to_chage = get_object_or_404(User, user=request.user), request.data['room_id'], request.data['target_date_week']
    room = get_object_or_404(Room, id=room_id)
    # only leader can change the rule
    if user.id == room.leader_id:
        # target date want to change
        seven_days = datetime.timedelta(days=7)
        if datetime.datetime.now().date() >= room.start_date + seven_days * target_date_week_to_chage:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            room.target_date = room.start_date + seven_days * target_date_week_to_chage
            room.save()
            return Response({'room_id': room.id}, status=status.HTTP_200_OK)


# # 방 조회하기 (추후 추가)
# @api_view(['GET'])
# def get_room(request):
#     user = get_object_or_404(User, user=request.user)
#     room = Room.objects.get(id=request.data['room_id'])
#     if UserRoom.objects.filter(user=user, room=room).exists():
#         serializer = RoomSerializer(room)
#         return Response({'Response': serializer.data}, status=status.HTTP_200_OK)
#     else:
#         return Response(status=status.HTTP_404_NOT_FOUND)


# # 방장 위임 (추후 추가)
# @api_view(['POST'])
# def leader_change(request):
#     user, room_id, username = get_object_or_404(User, user=request.user), request.data['room_id'], request.data['username']
#     room = get_object_or_404(Room, id=room_id)
#     user_to_change = get_object_or_404(User, username=username)
#     if user.id == room.leader_id:
#         room.leader_id = user_to_change.id
#         room.save()
#         return Response(status=status.HTTP_200_OK)
#     else:
#         return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
