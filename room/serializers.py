from rest_framework import serializers
from .models import Room
from .models import UserRoom

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('title', 'target_time', 'start_time', 'plan_half_fee', 'plan_no_fee', 'user_num', 'max_user_num', 'plan_period', 'negative_percent', 'room_code', 'leader_id')

class UserRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRoom
        fields = ('user', 'room')
