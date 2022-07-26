from django.urls import path
from .views import making_plan, myplan_content_endtime, user_plans

urlpatterns = [
    path('', making_plan),
    path('content/', myplan_content_endtime),
    path('user_plans/', user_plans)
]
