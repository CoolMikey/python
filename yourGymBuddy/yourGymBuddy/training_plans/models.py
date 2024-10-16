from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about_me = models.TextField(blank=True, null=True)
    is_trainer = models.BooleanField(default=False)  # New field to define if the user is a trainer

    def __str__(self):
        return self.user.username



class Exercise(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Set(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    percentage_of_best = models.DecimalField(max_digits=5, decimal_places=2)
    reps = models.PositiveIntegerField()

class WorkoutPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_by_trainer = models.BooleanField(default=False)  # New field to track trainer assignments

    def __str__(self):
        return f'{self.title} -- Created by {self.user.username}'

class CompletedSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise_set = models.ForeignKey(Set, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Weight used by the user
    reps = models.PositiveIntegerField(null=True, blank=True)  # Reps the user completed
    date_completed = models.DateTimeField(auto_now_add=True)  # When the user completed the set

    def __str__(self):
        return f"{self.user.username} - {self.exercise_set.exercise.name} on {self.date_completed}"
