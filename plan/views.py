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
from .models import Plan
from .models import Detail_Plan

from .serializers import PlanSerializer
from .serializers import DetailPlanSerializer

@api_view(['POST'])
def making_plan(request):
    room = Room.objects.get(id=request.data['room_id'])
    plan = Plan.objects.create(
        room=room,
        plan_start_time=request.data['plan_start_time'],
        week=1,
        end_time=datetime.datetime.strptime(request.data['plan_start_time'], "%Y-%m-%d")+datetime.timedelta(days=room.plan_period),
        revision_request=0
        )
    plan.save()
    return Response({'plan_id': plan.id})


@api_view(['POST'])
def making_detail_plan(request):
    user = get_object_or_404(User, user=request.user)
    plan = Plan.objects.get(id=request.data['plan_id'])
    detail_plan = Detail_Plan.objects.create(
        user=user,
        plan=plan,
        content=request.data['content'],
        peer_negative_review=0
    )
    detail_plan.save()
    
    return Response({"detail_plan_id": detail_plan.id})


@api_view(['GET'])
def all_detail_plan(request):
    user = get_object_or_404(User, user=request.user)
    plan = Plan.objects.get(id=request.data['plan_id'])
    detail_plan = Detail_Plan.objects.filter(user=user, plan=plan)
    d_plan_list = serializers.serialize('json', detail_plan)
    return HttpResponse(d_plan_list, content_type="text/json-coomment-filtered")


@api_view(['GET'])
def all_plan(request):
    user = get_object_or_404(User, user=request.user)
    room = Room.objects.get(id=request.data['room_id'])
    plan = Plan.objects.filter(room=room)
    if UserRoom.objects.filter(user=user, room=room).exists():
        plan_list = serializers.serialize('json', plan)
        return HttpResponse(plan_list, content_type="text/json-coomment-filtered")
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH', 'DELETE'])
def plan_patch_delete(request):
    user = get_object_or_404(User, user=request.user)
    d_plan = Detail_Plan.objects.filter(id=request.data['detail_plan_id'], user=user)
    if d_plan.exists():
        pass
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PATCH':
        serializer = DetailPlanSerializer(d_plan.first(), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        d_plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)