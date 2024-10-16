from django.shortcuts import render, redirect, get_object_or_404
from .models import WorkoutPlan, Set, Exercise,CompletedSet  
from .forms import SetForm, WorkoutPlanForm, RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib import messages

from itertools import groupby
from django.utils.timezone import localtime
from django.contrib.auth.models import User

from .forms import ProfileForm
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from .models import Profile  # Import the Profile model

import matplotlib.pyplot as plt
from io import BytesIO
import base64
from .models import CompletedSet
from .forms import ExerciseSelectionForm


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PlanAssignmentForm
from .models import WorkoutPlan
from .forms import UserRegistrationForm

@login_required
def assign_workout_plan(request):
    if not request.user.profile.is_trainer:
        return redirect('home')

    if request.method == 'POST':
        form = PlanAssignmentForm(request.POST)
        if form.is_valid():
            selected_user = form.cleaned_data['user']
            selected_plan = form.cleaned_data['workout_plan']
            
            # Create a new plan instance for the user, but mark it as assigned by the trainer
            new_plan = WorkoutPlan.objects.create(
                user=selected_user,
                title=selected_plan.title,
                assigned_by_trainer=True,  # Mark as assigned by trainer
            )
            new_plan.sets.set(selected_plan.sets.all())  # Copy sets from original plan
            new_plan.save()

            return redirect('home')
    else:
        form = PlanAssignmentForm()

    return render(request, 'training_plans/assign_workout_plan.html', {'form': form})

@login_required
def view_user_plans(request):
    user = request.user

    # Filter plans based on user input (created or assigned by trainer)
    filter_type = request.GET.get('filter', 'all')

    if filter_type == 'created':
        # Filter for plans created by the user
        workout_plans = WorkoutPlan.objects.filter(user=user, assigned_by_trainer=False)
    elif filter_type == 'assigned':
        # Filter for plans assigned by a trainer
        workout_plans = WorkoutPlan.objects.filter(user=user, assigned_by_trainer=True)
    else:
        # Show all plans by default
        workout_plans = WorkoutPlan.objects.filter(user=user)

    return render(request, 'training_plans/view_user_plans.html', {
        'workout_plans': workout_plans,
        'filter_type': filter_type,
    })


@login_required
def progress_graph(request):
    form = ExerciseSelectionForm(user=request.user)
    graph = None

    if request.method == 'POST':
        form = ExerciseSelectionForm(request.user, request.POST)
        if form.is_valid():
            selected_exercise = form.cleaned_data['exercise']

            # Filter the user's completed sets by the selected exercise
            completed_workouts = CompletedSet.objects.filter(user=request.user, exercise_set__exercise=selected_exercise).order_by('date_completed')

            # Prepare data for the graph
            dates = [workout.date_completed for workout in completed_workouts]
            weights = [workout.weight for workout in completed_workouts]

            # Create the graph
            plt.figure(figsize=(10, 5))
            plt.plot(dates, weights, marker='o', linestyle='-', color='b')
            plt.title(f'Progress for {selected_exercise.name} Over Time')
            plt.xlabel('Date')
            plt.ylabel('Weight (kg)')
            plt.xticks(rotation=45)

            # Save the plot to a string in memory
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            graph = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'training_plans/progress_graph.html', {
        'form': form,
        'graph': graph,
    })


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account_page')  # Redirect to account page after saving
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'training_plans/edit_profile.html', {'form': form})


def home(request):
    # If the user is logged in, redirect them to their account page
    if request.user.is_authenticated:
        return redirect('account_page')  # Redirect to account page
    # If not logged in, render the landing page
    return render(request, 'landing_page.html')

@login_required
@login_required
def account_page(request):
    user = request.user
    # Check if the user has any workout plans
    user_workout_plans = WorkoutPlan.objects.filter(user=user)

    # Get all the user's completed sets (previous workouts)
    completed_workouts = CompletedSet.objects.filter(user=user).order_by('-date_completed')

    # Group completed workouts by date (treating them as a single session)
    grouped_workouts = {}
    for date, exercises in groupby(completed_workouts, key=lambda x: localtime(x.date_completed).date()):
        grouped_workouts[date] = list(exercises)

    no_plans = not user_workout_plans.exists()

    return render(request, 'account_page.html', {
        'user': user,
        'user_workout_plans': user_workout_plans,
        'no_plans': no_plans,
        'grouped_workouts': grouped_workouts,  # Pass grouped workouts to the template
    })


@login_required
def workout_history(request):
    # Fetch all completed workouts for the logged-in user
    completed_workouts = CompletedSet.objects.filter(user=request.user).order_by('-date_completed')

    return render(request, 'training_plans/workout_history.html', {
        'completed_workouts': completed_workouts,
    })

def user_profile(request, user_id):
    # Get the user's profile information and their workout history
    user = get_object_or_404(User, id=user_id)
    completed_workouts = CompletedSet.objects.filter(user=user).order_by('-date_completed')

    return render(request, 'training_plans/user_profile.html', {
        'profile_user': user,
        'completed_workouts': completed_workouts,
    })

# Create a Workout Plan
@login_required
def create_workout_plan(request):
    if request.method == 'POST':
        workout_form = WorkoutPlanForm(request.POST)
        if workout_form.is_valid():
            workout_plan = workout_form.save(commit=False)
            workout_plan.user = request.user
            workout_plan.save()

            # Redirect to the page where the user can add sets
            return redirect('add_sets', workout_plan_id=workout_plan.id)
    else:
        workout_form = WorkoutPlanForm()

    return render(request, 'training_plans/create_workout_plan.html', {'workout_form': workout_form})

@login_required
def add_sets(request, workout_plan_id):
    workout_plan = WorkoutPlan.objects.get(id=workout_plan_id)
    
    # Initial form values (default is empty if no values need to be retained)
    initial_data = {}

    if request.method == 'POST':
        set_form = SetForm(request.POST)
        if set_form.is_valid():
            new_set = set_form.save()  # Save the new set
            workout_plan.sets.add(new_set)
            workout_plan.save()

            # If "keep_values" is checked, retain the current form data for the next form
            if set_form.cleaned_data.get('keep_values'):
                # Retain the exercise, percentage of personal best, and reps for the next form
                initial_data = {
                    'exercise': set_form.cleaned_data['exercise'],
                    'percentage_of_best': set_form.cleaned_data['percentage_of_best'],
                    'reps': set_form.cleaned_data['reps'],
                }

            # Reinitialize the form with either empty data or the retained data
            set_form = SetForm(initial=initial_data)

            # Redirect to the same page to avoid form resubmission on page refresh
            return redirect('add_sets', workout_plan_id=workout_plan.id)

    else:
        # Initialize an empty form when first loading the page
        set_form = SetForm(initial=initial_data)

    return render(request, 'training_plans/add_sets.html', {
        'workout_plan': workout_plan,
        'set_form': set_form,
    })

# View list of workout plans
@login_required
def view_workout_plans(request):
    workout_plans = WorkoutPlan.objects.filter(user=request.user)
    return render(request, 'training_plans/view_workout_plans.html', {'workout_plans': workout_plans})

@login_required
def modify_workout_list(request):
    workout_plans = WorkoutPlan.objects.filter(user=request.user)
    return render(request, 'training_plans/modify_workout_list.html', {'workout_plans': workout_plans})

@login_required
def modify_workout(request, workout_plan_id):
    # Get the original workout plan that the user wants to modify
    original_plan = get_object_or_404(WorkoutPlan, id=workout_plan_id, user=request.user)
    
    if request.method == 'POST':
        # Check if the user provided a new title for the modified workout plan
        new_title = request.POST.get('title')
        if not new_title:
            # Display an error if no new title is provided
            return render(request, 'training_plans/modify_workout.html', {
                'workout_plan': original_plan,
                'error_message': "Please provide a new title for the workout plan.",
            })
        
        # Create a copy of the original workout plan with the new title
        new_plan = WorkoutPlan.objects.create(
            user=request.user,
            title=new_title,
        )
        
        # Copy existing sets from the original workout plan to the new one
        for workout_set in original_plan.sets.all():
            new_set = Set.objects.create(
                exercise=workout_set.exercise,
                percentage_of_best=workout_set.percentage_of_best,
                reps=workout_set.reps
            )
            new_plan.sets.add(new_set)
        
        # If the user adds a new exercise
        if 'new_exercise' in request.POST:
            exercise_id = request.POST.get('exercise')
            percentage_of_best = request.POST.get('new_percentage_of_best')
            reps = request.POST.get('new_reps')
            
            if exercise_id and percentage_of_best and reps:
                new_exercise = Exercise.objects.get(id=exercise_id)
                new_set = Set.objects.create(
                    exercise=new_exercise,
                    percentage_of_best=percentage_of_best,
                    reps=reps
                )
                new_plan.sets.add(new_set)
        
        # Handle removing an exercise if the user clicked the "remove" button
        if 'remove_set' in request.POST:
            set_id = request.POST.get('remove_set')
            set_to_remove = Set.objects.get(id=set_id)
            new_plan.sets.remove(set_to_remove)
        
        # Save the new workout plan
        new_plan.save()
        
        return redirect('view_all_workout_plans')  # Redirect to view all workout plans after modifications
    
    else:
        # Pre-fill the form with the original workout plan details
        exercises = Exercise.objects.all()  # Load all exercises for adding a new one
        return render(request, 'training_plans/modify_workout.html', {
            'workout_plan': original_plan,
            'exercises': exercises
        })



@login_required
def pick_exercises(request):
    # Allow users to pick exercises to add to their workout
    sets = Set.objects.all()
    if request.method == 'POST':
        selected_sets = request.POST.getlist('sets')
        return redirect('track_workout', set_ids=','.join(selected_sets))

    return render(request, 'training_plans/pick_exercises.html', {
        'sets': sets,
    })

@login_required
def track_workout(request, set_ids):
    set_ids = set_ids.split(',')
    sets = Set.objects.filter(id__in=set_ids)

    if request.method == 'POST':
        for set_id in set_ids:
            set_obj = Set.objects.get(id=set_id)
            weight = request.POST.get(f'weight_{set_id}')
            reps = request.POST.get(f'reps_{set_id}')
            
            # Create CompletedSet entry
            completed_set = CompletedSet.objects.create(
                user=request.user,
                exercise_set=set_obj,
                weight=weight,
                reps=reps
            )
        
        return redirect('view_completed_sets')

    return render(request, 'training_plans/track_workout.html', {
        'sets': sets,
    })

    
@login_required
def view_completed_sets(request):
    # View and print completed exercises
    completed_sets = CompletedSet.objects.filter(user=request.user).order_by('-date_completed')
    return render(request, 'training_plans/view_completed_sets.html', {
        'completed_sets': completed_sets,
    })

@login_required
def view_all_workout_plans(request):
    # Get all workout plans
    all_workout_plans = WorkoutPlan.objects.all()

    # Get the user's workout plans
    user_workout_plans = WorkoutPlan.objects.filter(user=request.user)

    # Filter community plans (plans not owned by the user)
    community_plans = WorkoutPlan.objects.exclude(user=request.user)

    if request.method == 'POST':
        # Handle adding a plan to the user's list
        plan_id = request.POST.get('add_plan')
        if plan_id:
            selected_plan = WorkoutPlan.objects.get(id=plan_id)
            # Add the plan to the user's workout plans
            new_plan = WorkoutPlan.objects.create(
                user=request.user,
                title=selected_plan.title,
                # Copy any other fields you want from the selected plan
            )
            new_plan.sets.set(selected_plan.sets.all())  # Copy the sets
            new_plan.save()
            return redirect('view_all_workout_plans')  # Reload the page to reflect changes

    return render(request, 'training_plans/view_all_workout_plans.html', {
        'user_workout_plans': user_workout_plans,
        'community_plans': community_plans,
    })

    
@login_required
def user_workout_plans(request):
    # Fetch all workout plans that belong to the logged-in user
    user_plans = WorkoutPlan.objects.filter(user=request.user)

    return render(request, 'training_plans/user_workout_plans.html', {
        'user_plans': user_plans,
    })


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            # Create a profile for the user
            is_trainer = form.cleaned_data.get('is_trainer', False)
            profile = Profile.objects.create(user=user, is_trainer=is_trainer)

            # Log the user in or redirect as needed
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')  # Redirect to home or any other page after login
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})