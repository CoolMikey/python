from django.shortcuts import render
from .models import TrainingPlan
from django.contrib.auth.decorators import login_required

@login_required
def training_plan_list(request):
    plans = TrainingPlan.objects.all()
    return render(request, 'training_plans/training_plan_list.html', {'plans': plans})
