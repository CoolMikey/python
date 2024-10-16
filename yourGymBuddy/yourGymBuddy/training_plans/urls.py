from django.urls import path
from . import views

urlpatterns = [
    # path('', views.training_plan_list, name='training_plan_list'),
    path('create/', views.create_workout_plan, name='create_workout_plan'),
    path('add_sets/<int:workout_plan_id>/', views.add_sets, name='add_sets'),
    # path('', views.view_all_workout_plans, name='view_all_workout_plans'),  # Correct URL name
]
