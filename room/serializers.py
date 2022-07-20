from rest_framework import serializers
from .models import Room
from .models import UserRoom


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('title', 'target_date', 'max_user_num', 'rule_num', 'user_num', 'start_date', 'leader_id', 'room_code')


class UserRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoom
        fields = ('user', 'room', 'percent_sum')
