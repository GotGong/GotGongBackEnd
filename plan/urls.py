from django.urls import path
from .views import making_plan, myplan_content_endtime, user_plans, plan_dislike, ranking, refund_calculation, my_detail_plans

urlpatterns = [
    path('', making_plan),
    path('content/', myplan_content_endtime),
    path('user_plans/', user_plans),
    path('dislike/', plan_dislike),
    path('rank/', ranking),
    path('refund/', refund_calculation),
    path('details/', my_detail_plans)
]
