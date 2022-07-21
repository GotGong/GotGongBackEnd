from rest_framework import serializers
from .models import Plan, DetailPlan, UserPlan, UserPlanDislike, UserDetailPlanDislike

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class DetailPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailPlan
        fields = '__all__'


class UserPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlan
        fields = '__all__'


class UserPlanDislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlanDislike
        fields = '__all__'


class UserDetailPlanDislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetailPlanDislike
        fields = '__all__'
