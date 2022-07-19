from django.urls import path
from .views import making_plan, making_detail_plan, all_detail_plan, all_plan, plan_patch_delete

urlpatterns = [
    path('start_study/', making_plan),
    path('new_plan/', making_detail_plan),
    path('all_detail/', all_detail_plan),
    path('all_plan/', all_plan),
    path('', plan_patch_delete),
]
