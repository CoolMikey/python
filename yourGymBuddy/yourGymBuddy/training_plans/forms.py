from django import forms
from .models import WorkoutPlan, Set, Exercise, CompletedSet
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Profile
from django import forms
from .models import CompletedSet

from .models import Exercise  # Assuming there's an Exercise model

from django import forms
from django.contrib.auth.models import User
from .models import WorkoutPlan

from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirm Password")
    is_trainer = forms.BooleanField(required=False, label="Sign up as a Trainer", widget=forms.CheckboxInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data


class PlanAssignmentForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),  # All users
        label="Select User",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    workout_plan = forms.ModelChoiceField(
        queryset=WorkoutPlan.objects.all(),  # All workout plans
        label="Select Workout Plan",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ExerciseSelectionForm(forms.Form):
    exercise = forms.ModelChoiceField(
        queryset=None,  # We will populate this queryset in the view
        label="Choose Exercise",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, user, *args, **kwargs):
        super(ExerciseSelectionForm, self).__init__(*args, **kwargs)
        # Get distinct exercises the user has done and return actual Exercise objects
        self.fields['exercise'].queryset = Exercise.objects.filter(
            id__in=CompletedSet.objects.filter(user=user).values_list('exercise_set__exercise', flat=True).distinct()
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['about_me']


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Adding an email field

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class CompletedSetForm(forms.ModelForm):
    class Meta:
        model = CompletedSet
        fields = ['weight', 'reps']

class SetForm(forms.ModelForm):
    exercise = forms.ModelChoiceField(queryset=Exercise.objects.all(), label='Exercise')
    percentage_of_best = forms.DecimalField(label='Percentage of Personal Best (%)')
    reps = forms.IntegerField(label='Reps')
    keep_values = forms.BooleanField(required=False, label='Keep these values for the next set')

    class Meta:
        model = Set
        fields = ['exercise', 'percentage_of_best', 'reps']


class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = ['title']
