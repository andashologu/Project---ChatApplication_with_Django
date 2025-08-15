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
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from .models import CustomUser



@method_decorator(never_cache, name='dispatch')
class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm  # Use your custom form
    #template_name = 'registration/login.html'
    template_name = 'registration/webflow/login_template.html'
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

@never_cache
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        errors = {}

        # Basic validations
        if not username:
            errors['username'] = 'Username is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not password1 or not password2:
            errors['password'] = 'Password is required.'
        elif password1 != password2:
            errors['password'] = 'Passwords do not match.'
        elif len(password1) < 6:
            errors['password'] = 'Password must be at least 6 characters.'

        # Check uniqueness
        if CustomUser.objects.filter(username=username).exists():
            errors['username'] = 'Username already exists.'
        if CustomUser.objects.filter(email=email).exists():
            errors['email'] = 'Email already exists.'

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # Create custom user
        user = CustomUser.objects.create(
            username=username,
            first_name=firstname,
            last_name=lastname,
            email=email,
            password=make_password(password1)
        )

        # Optionally, you could log the user in immediately here

        return JsonResponse({
            'success': True,
            'redirect_url': reverse_lazy('login')  # redirect after signup
        })

    # GET request → render signup template
    return render(request, 'authapp/webflow/signup_template.html')
