from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

from django.contrib.auth.views import LoginView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse

from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.urls import reverse_lazy
from .forms import CustomAuthenticationForm
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm  # Use your custom form
    template_name = 'registration/login.html'
    success_url = reverse_lazy('chat')

    def form_valid(self, form):
        # Log the user in
        super().form_valid(form)
        print("login view")
        # Generate JWT tokens
        user = form.get_user()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Return tokens and redirect URL as JSON
        return JsonResponse({
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'redirect_url': self.success_url,
        })

    def form_invalid(self, form):
        # Return form errors as JSON response
        return JsonResponse({
            'success': False,
            'errors': form.errors,
        }, status=400)

class CustomLogoutView(LogoutView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    template_name = 'registration/logout.html'  # Specify the template to be rendered after logout

@login_required  # Requires user to be authenticated via session
def home_view(request):
    return render(request, 'home.html', {'message': 'Welcome to the home page!'})

def signup(request):
    return render(request, 'authapp/signup.html')