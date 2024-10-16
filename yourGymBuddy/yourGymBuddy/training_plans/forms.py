from django import forms
from .models import Set, WorkoutPlan, Exercise, PersonalBest

class SetForm(forms.ModelForm):
    exercise = forms.ModelChoiceField(queryset=Exercise.objects.all(), label='Exercise')
    percentage_of_best = forms.DecimalField(label='Percentage of Personal Best (%)')
    reps = forms.IntegerField(label='Reps')

    class Meta:
        model = Set
        fields = ['exercise', 'percentage_of_best', 'reps']

class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = ['title']
