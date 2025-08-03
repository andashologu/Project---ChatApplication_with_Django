from django.db import models
from django.conf import settings  # Import to reference custom user model
from django.utils import timezone
from django.db import models
from django.conf import settings  # Reference to CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVectorField

class Message(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    search_vector = SearchVectorField(null=True)  # For full-text search

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}"

    class Meta:
        ordering = ['-timestamp']

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # One-to-one relationship with CustomUser
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

# Automatically create or update the Profile when a CustomUser is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)  # Create profile on user creation
    instance.profile.save()  # Save the profile whenever the user is saved
