from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.postgres.search import SearchVectorField

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(Group, related_name='customuser_set')  # Change related_name to avoid clash
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_permissions_set')  # Change related_name to avoid clash
    """
    Custom user model with a unique email field and the default unique username.
    """
    email = models.EmailField(unique=True)  # Make sure email is unique
    search_vector = SearchVectorField(null=True)  # For full-text search

    def __str__(self):
        return self.username  # or return self.email, if that's preferred


