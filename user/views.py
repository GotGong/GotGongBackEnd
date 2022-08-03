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
    # authenticate 사용해서 auth의 User 인증
    user = authenticate(username=request.data['userid'], password=request.data['password'])
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED) # 권한 없음
    try:
        # user를 통해 token get
        token = Token.objects.get(user=user)
    except:
        # [FIX]: token이 없는 경우 (token 생성 이후 기간이 지나 token이 만료되어 사라진 경우) token 재생성
        token = Token.objects.create(user=user)
    return Response({"Token": token.key, "user_name": user.username})


# 사용자 회원가입
@api_view(['POST'])
def signup(request):
    # auth의 User 저장
    user = User.objects.create_user(username=request.data['userid'], password=request.data['password'])
    token = Token.objects.create(user=user) # Token Create
    user.save() # auth의 User 저장
    
    # User Entity 저장
    username, email = request.data['username'], request.data['email']
    user = models.User(user=user, username=username, email=email)
    user.save() # Model의 User Entity 저장 (auth의 User와 1대 1 매핑으로 연결되어있음)
    return Response({"Token": token.key, "user_name": user.username}) # 이 Token 값은 FrontEnd에 저장해두고 인증/인가 시 사용함


# 사용자 이름변경 or 사용자 삭제
@api_view(['GET', 'PATCH', 'DELETE'])
def get_patch_delete(request):
    if request.method == 'GET':
        user = get_object_or_404(User, id=request.user.id)
        return Response({'email': user.email, 'userid': user.userid, 'password': user.password, 'username': user.username}, status=status.HTTP_200_OK)
        
    elif request.method == 'PATCH':
        user, userid_to_change, password_to_change, username_to_change = get_object_or_404(models.User, user=request.user), request.data['userid'], request.data['password'], request.data['username']
        user.userid = userid_to_change
        user.password = password_to_change
        user.username = username_to_change
        user.save()
        return Response(status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        # auth의 User가 삭제되면 Model의 User 또한 삭제됨 (CASCADE)
        user = get_object_or_404(User, id=request.user.id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 아이디 중복 체크
@api_view(['POST'])
def duplicationcheck(request):
    userid = request.data['userid']
    try:
        user = get_object_or_404(User, username=userid)
    except:
        return Response(False, status=status.HTTP_200_OK)
    return Response(True, status=status.HTTP_200_OK)
