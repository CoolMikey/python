from django.urls import path
from . import views

urlpatterns = [
    path('', views.training_plan_list, name='training_plan_list'),
]
