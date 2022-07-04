from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from . import models
from .serializers import UserSerializer

# 사용자 로그인
@api_view(['POST'])
def signin(request):
    # authenticate 사용해서 account의 User 인증
    user = authenticate(username=request.data['userid'], password=request.data['password'])
    if user is not None:
        token = Token.objects.get(user=user)
        return Response({"Token": token.key})
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED) # 권한 없음


# 사용자 회원가입
@api_view(['POST'])
def signup(request):
    # account의 User 저장
    user = User.objects.create_user(username=request.data['userid'], password=request.data['password'])
    token = Token.objects.create(user=user) # Token Create
    user.save() # account의 User 저장
    
    # User Entity 저장
    nickname, email = request.data['nickname'], request.data['email']
    user = models.User(user=user, nickname=nickname, email=email)
    user.save() # Model의 User Entity 저장 (account의 User와 1대 1 매핑으로 연결되어있음)
    return Response({"Token": token.key}) # 이 Token 값은 FrontEnd에 저장해두고 인증/인가 시 사용함


# 사용자 이름변경 or 사용자 삭제
@api_view(['PATCH', 'DELETE'])
def patch_delete(request):
    if request.method == 'PATCH':
        user = get_object_or_404(models.User, user=request.user)
        # partial=True이므로 PATCH method가 가능함
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        user = get_object_or_404(models.User, user=request.user)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 테스트용!!!
# (HTTP Header에 Authentication에 Token (토큰값)을 넣어 요청을 보내면 user와 token 값을 알 수 있음)
@api_view(['GET'])
def check(request):
    print(request.user)
    print(request.auth)
    return Response('hi')
