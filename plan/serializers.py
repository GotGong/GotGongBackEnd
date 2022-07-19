from rest_framework import serializers
from .models import Plan, Detail_Plan

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ('room', 'plan_start_time', 'plan_status', 'end_time', 'week', 'revision_request')


class DetailPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detail_Plan
        fields = ('plan', 'user', 'content', 'peer_negative_review', 'self_check')