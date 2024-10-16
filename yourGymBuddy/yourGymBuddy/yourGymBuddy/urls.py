"""
URL configuration for yourGymBuddy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from training_plans import views
from django.contrib.auth import views as auth_views

from django.urls import path, include
from django.contrib.auth import views as auth_views
from training_plans import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),  # Home and Landing Page
    path('account/', views.account_page, name='account_page'),

    # Workout Plan Management
    path('plans/', include([
        path('', views.view_all_workout_plans, name='view_all_workout_plans'),  # View all workout plans
        
        path('create/', views.create_workout_plan, name='create_workout_plan'),  # Create a workout plan
        path('add_sets/<int:workout_plan_id>/', views.add_sets, name='add_sets'),  # Add sets to a workout plan
        path('user/', views.user_workout_plans, name='user_workout_plans'),  # View user's workout plans
        path('modify/', views.modify_workout_list, name='modify_workout_list'),  # List workout plans to modify
        path('modify/<int:workout_plan_id>/', views.modify_workout, name='modify_workout'),  # Modify a workout plan
    ])),

    # Exercise Tracking and Completed Workouts
    path('exercises/', include([
        path('pick/', views.pick_exercises, name='pick_exercises'),  # Pick exercises
        path('track/<str:set_ids>/', views.track_workout, name='track_workout'),  # Track workout progress
        path('completed/', views.view_completed_sets, name='view_completed_sets'),  # View completed workouts
    ])),

    # Account Management (Register, Login, Logout)
    path('accounts/', include('django.contrib.auth.urls')),  # Django auth system
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),  # Custom login view
    path('signin/', views.custom_login, name='signin'),  # Custom login view
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # path('account/', views.account_page, name='account_page'),
    path('workout_history/', views.workout_history, name='workout_history'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('progress_graph/', views.progress_graph, name='progress_graph'),
    path('assign_plan/', views.assign_workout_plan, name='assign_workout_plan'),
]
