from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from authapp.models import CustomUser
from .models import Message
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .consumer import connected_users
from django.forms.models import model_to_dict
from django.db import models  # Make sure this is imported
from django.db.models import OuterRef, Subquery, Count, Max
from django.contrib.postgres.search import SearchVector, SearchQuery
from .documents import CustomUserDocument, MessageDocument

@login_required
def index(request):
    return render(request, 'chatapp/index.html')

from django.db.models import Q
from django.shortcuts import render

@login_required

# chatapp/views.py
def chats_view(request):
    current_user = request.user
    search_query = request.GET.get('q', '')  # Get search query
    connected_user_ids = list(connected_users.keys())

    if search_query:
        # Search for users by username, first_name, or last_name
        user_search = CustomUserDocument.search().query(
            "multi_match", query=search_query, fields=['username', 'first_name', 'last_name']
        )

        # Search for messages containing the search query
        message_search = MessageDocument.search().query(
            "multi_match", query=search_query, fields=['message', 'sender.username', 'recipient.username']
        )

        # Get users that match the search query from the user search
        user_ids = [hit.meta.id for hit in user_search if hit.username != current_user.username]  # Exclude current user
        users = CustomUser.objects.filter(id__in=user_ids)

        # Get users involved in matching messages (both sender and recipient)
        message_usernames = set(
            [hit.sender.username for hit in message_search if hit.sender.username != current_user.username] +  # Exclude current user
            [hit.recipient.username for hit in message_search if hit.recipient.username != current_user.username]  # Exclude current user
        )
        users_involved_in_messages = CustomUser.objects.filter(username__in=message_usernames)

        # Combine both user sets
        chats = users | users_involved_in_messages  # Union of both querysets

        print("done searching chats...")
    else:
        # Use ElasticSearch to get all users the current user has chatted with
        message_search = MessageDocument.search().filter(
            "bool", should=[
                {"term": {"sender.username": current_user.username}},
                {"term": {"recipient.username": current_user.username}}
            ]
        )

        # Get the usernames of the users involved in those messages
        message_usernames = set(
            [hit.sender.username for hit in message_search if hit.sender.username != current_user.username] +  # Exclude current user
            [hit.recipient.username for hit in message_search if hit.recipient.username != current_user.username]  # Exclude current user
        )

        # Fetch the users involved in the messages using the usernames
        chats = CustomUser.objects.filter(username__in=message_usernames).exclude(username=current_user.username).distinct()

    # Get last message and unread count using ElasticSearch
    last_message_subquery = Message.objects.filter(
        sender=current_user, recipient=OuterRef('pk')
    ).order_by('-timestamp').values('message')[:1]

    unread_count_subquery = Message.objects.filter(
        sender=OuterRef('pk'), recipient=current_user,
        status__in=['unread', 'sent', 'delivered']
    ).values('sender').annotate(unread_count=Count('id')).values('unread_count')

    # Annotate chats with the last message and unread count
    chats = chats.annotate(
        last_message=Subquery(last_message_subquery),
        unread_count=Subquery(unread_count_subquery, output_field=models.IntegerField())
    )

    # Prepare chat data for rendering
    chats_data = []
    chats_ids = []
    for chat in chats:
        chats_data.append({
            'chat': chat,
            'last_message': chat.last_message,
            'unread_count': chat.unread_count or 0,
            'status': "Online" if chat.id in connected_user_ids else "Offline"
        })
        chats_ids.append({
            'chat_id': chat.id
        })

    # Render the chat HTML using template
    print("rendering html...")
    chats_html = render_to_string('chatapp/components/chat.html', {
        'chats_data': chats_data,
        'search_query': search_query
    })

    return JsonResponse({
        'html': chats_html,
        'data': chats_ids
    })

@login_required
def chat_messages_view(request, contact_id):
    current_user = request.user
    contact = get_object_or_404(CustomUser, id=contact_id)

    # Get all messages between the current user and the contact
    messages = Message.objects.filter(
        Q(sender=current_user, recipient=contact) | Q(sender=contact, recipient=current_user)
    ).order_by('timestamp')

    # Mark 'unread', 'sent', and 'delivered' messages from the contact as 'read'
    unread_messages = messages.filter(sender=contact, recipient=current_user).filter(Q(status='unread') | Q(status='sent') | Q(status='delivered'))
    unread_messages.update(status='read')

    messages_html = render_to_string('chatapp/components/message.html', { #render_to_string does not perform an HTTP request. It is a Django utility function that renders a Django template into a string of HTML by combining the template with the context (data) you provide.
        'messages': messages,
        'current_user': current_user
    })
   
    message_list = list(messages.values())
    data = {
        'messages': message_list,
        'current_user': model_to_dict(current_user)
        }
    
    return JsonResponse({
        'html': messages_html,
        'data': data,
    }, safe = False)

@api_view(['POST'])  # This ensures the view only accepts POST requests
@authentication_classes([JWTAuthentication])  # Use JWT for authentication
@permission_classes([IsAuthenticated])  # Ensure user is authenticated via JWT
def search_contacts(request):
    query = request.data.get('q', '')  # Get the search term from the request

    if query:
        # Perform search on username, firstname, and lastname with case-insensitive partial matches
        results = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).values('username', 'first_name', 'last_name')  # Limit the fields returned
        return JsonResponse(list(results), safe=False)
    return JsonResponse({'error': 'No query provided'}, status=400)

