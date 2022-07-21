from django.contrib import admin
from .models import Plan, DetailPlan, UserPlan, UserPlanDislike, UserDetailPlanDislike

admin.site.register(Plan)
admin.site.register(DetailPlan)
admin.site.register(UserPlan)
admin.site.register(UserPlanDislike)
admin.site.register(UserDetailPlanDislike)
