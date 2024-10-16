from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Exercise, Set, WorkoutPlan, CompletedSet

# Inline profile editing in the User admin panel
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'

# Custom User admin to display 'is_trainer' from the Profile model
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)  # Add Profile model inline to the User model
    
    # Show is_trainer in the user list
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_trainer')

    # Function to access the is_trainer field in the Profile model
    def is_trainer(self, obj):
        return obj.profile.is_trainer
    is_trainer.boolean = True  # Display as a boolean (True/False with a checkmark)
    is_trainer.short_description = 'Trainer'

# Unregister the default User admin and register the custom User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models in the admin panel
admin.site.register(Profile)
admin.site.register(Exercise)
admin.site.register(Set)
admin.site.register(WorkoutPlan)
admin.site.register(CompletedSet)
