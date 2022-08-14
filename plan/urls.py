from django.urls import path
from .views import making_plan, myplan_content_endtime, user_plans, plan_dislike, ranking, refund_calculation, my_detail_plans, plan_patch_delete, dplan_dislike_and_check, other_user_plans

urlpatterns = [
    path('', making_plan),
    path('dislike/', plan_dislike),
    path('change/', plan_patch_delete),
    path('dplan_dislike/', dplan_dislike_and_check),
    path('content/<int:id>/', myplan_content_endtime),
    path('refund/<int:id>/', refund_calculation),
    path('rank/<int:id>/', ranking),
    path('details/<int:id>/', my_detail_plans),
    path('user_plans/<int:id>/', user_plans),
    path('other_user_plans/', other_user_plans)
]
