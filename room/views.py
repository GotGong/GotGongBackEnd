from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from rest_framework import status
from django.utils import timezone

from user.models import User
from . import models
from .models import Room
from .models import UserRoom
from .serializers import RoomSerializer

import uuid
import base64
import codecs

# WUJtQT09와 같은 형태로 랜덤 코드 생성
def generate_random_slug_code(length=15):  # length는 1-32사이에 존재해야 함.
    return base64.urlsafe_b64encode(       # url에서도 랜덤 코드를 사용가능하게 하기 위한 함수
        codecs.encode(uuid.uuid4().bytes, "base64").rstrip() # base64로 인코딩
    ).decode()[:length] # 바이트스트링 타입을 문자열로 활용하기 위한 코드


@api_view(['POST','PATCH', 'DELETE'])
def post_patch_delete(request):
    if request.method == 'PATCH':
        user, room_id, title_to_change = get_object_or_404(User, user=request.user), request.data['room_id'], request.data['title']
        room = get_object_or_404(Room, id=room_id)
        if user.id == room.leader_id:
            room.title = title_to_change
            room.save()
            return Response(data=room_id ,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif request.method == 'DELETE':
        rooms = Room.objects.all()
        now_date_time = timezone.now()
        for room in rooms:
            if room.target_time < now_date_time:
                room.delete()
        return Response(status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        user = get_object_or_404(User, user=request.user)

        code=generate_random_slug_code()
        if Room.objects.filter(room_code=code).exists():
            code=generate_random_slug_code()

        room = Room.objects.create(
            title=request.data['title'], 
            target_time=request.data['target_time'],
            plan_half_fee=request.data['plan_half_fee'],
            plan_no_fee=request.data['plan_no_fee'],
            max_user_num=5,
            plan_period=request.data['plan_period'],
            negative_percent=request.data['negative_percent'],
            user_num=1,
            room_code=code,
            leader_id=user.id
            )
        room.save()
        
        userroom = models.UserRoom(user=user, room=room)
        userroom.save() 

        return Response({"Room_code": code})


@api_view(['POST'])
def enter_bycode (request):
    user = get_object_or_404(User, user=request.user)
    room_code = request.data['room_code']
    room = Room.objects.get(room_code=room_code)
    if Room.objects.filter(room_code=room_code).exists():
        if UserRoom.objects.filter(user=user, room=room).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            room.user_num += 1
            room.save()
            userroom = models.UserRoom(user=user, room=room)
            userroom.save()
            return Response({"Room_id": room.id})
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def my_room(request):
    # UserRoom 테이블에서 user가 참여한 room의 id 찾기
    user = get_object_or_404(User, user=request.user)
    userrooms = UserRoom.objects.filter(user=user)
    rooms_list = []
    for userroom in userrooms:
        room = userroom.room
        rooms = Room.objects.filter(id=room.id).values('id', 'title', 'start_time', 'user_num', 'max_user_num', 'leader_id')
        rooms_list.append(rooms)

    return Response({'Response': rooms_list})


@api_view(['GET'])
def get_room(request):
    user = get_object_or_404(User, user=request.user)
    room = Room.objects.get(id=request.data['room_id'])
    if UserRoom.objects.filter(user=user, room=room).exists():
        serializer = RoomSerializer(room)
        return Response({'Response': serializer.data})
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

    