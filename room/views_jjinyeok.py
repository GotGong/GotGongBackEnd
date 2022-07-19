from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone

from user.models import User
from .models import Room, UserRoom


# 방장 위임
@api_view(['POST'])
def leader_change(request):
    user, room_id, username = get_object_or_404(User, user=request.user), request.data['room_id'], request.data['username']
    room = get_object_or_404(Room, id=room_id)
    user_to_change = get_object_or_404(User, username=username)
    if user.id == room.leader_id:
        room.leader_id = user_to_change.id
        room.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 방 참여하기 - 이미 참여한 방으로 접속
@api_view(['POST'])
def enter(request):
    user, room_id = get_object_or_404(User, user=request.user), request.data['room_id']
    room = get_object_or_404(Room, id=room_id)
    user_room = get_object_or_404(UserRoom, user=user, room=room)
    if user_room:
        return Response(data=room_id ,status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
