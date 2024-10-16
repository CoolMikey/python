from django.db import models
from django.contrib.auth.models import User

class Exercise(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class PersonalBest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    personal_best = models.DecimalField(max_digits=5, decimal_places=2)  # Store user's personal best for each exercise in kilograms or pounds

    def __str__(self):
        return f'{self.user.username} - {self.exercise.name} - {self.personal_best}'

class Set(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    percentage_of_best = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage of personal best
    reps = models.PositiveIntegerField()  # Number of reps for the set

class WorkoutPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    sets = models.ManyToManyField(Set)  # A workout plan consists of many sets
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title