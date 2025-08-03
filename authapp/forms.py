# forms.py
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, get_user_model

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser

class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form that allows users to log in with either their username or email.
    """
    username = forms.CharField(label="Username or Email")

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        # Use the custom user model instead of the default User model
        UserModel = get_user_model()

        if username_or_email and password:
            # Check if the input is an email
            if '@' in username_or_email:
                try:
                    # Get the user by email using the custom user model
                    user = UserModel.objects.get(email=username_or_email)
                    # Authenticate using the username
                    self.user_cache = authenticate(username=user.username, password=password)
                except UserModel.DoesNotExist:
                    raise forms.ValidationError("Invalid email or password")
            else:
                # Authenticate by username
                self.user_cache = authenticate(username=username_or_email, password=password)

            if self.user_cache is None:
                raise forms.ValidationError("Invalid username/email or password")
        else:
            raise forms.ValidationError("Both fields are required")

        return self.cleaned_data

    def get_user(self):
        return self.user_cache