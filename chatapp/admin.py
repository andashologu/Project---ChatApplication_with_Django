# admin.py
from django.contrib import admin
from .models import Message, Profile

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'message', 'timestamp', 'status')
    search_fields = ('sender__username', 'recipient__username', 'message')
    list_filter = ('status', 'timestamp')
    ordering = ['-timestamp']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'location', 'birth_date')
    search_fields = ('user__username', 'bio')

# Register each model separately with its admin class
admin.site.register(Message, MessageAdmin)
admin.site.register(Profile, ProfileAdmin)
