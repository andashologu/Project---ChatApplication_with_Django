# chatapp/documents.py
from django_elasticsearch_dsl import Document, fields, Index
from .models import Message
from authapp.models import CustomUser

# Define the index for users
user_index = Index('users')

@user_index.doc_type
class CustomUserDocument(Document):
    username = fields.TextField()
    first_name = fields.TextField()
    last_name = fields.TextField()

    class Django:
        model = CustomUser
        fields = []  # No additional fields are necessary

message_index = Index('messages')

@message_index.doc_type
class MessageDocument(Document):
    sender = fields.ObjectField(properties={
        'username': fields.TextField(),
    })
    recipient = fields.ObjectField(properties={
        'username': fields.TextField(),
    })
    message = fields.TextField()

    class Django:
        model = Message
        fields = ['timestamp']