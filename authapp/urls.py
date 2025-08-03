from django.urls import path
from .views import home_view
from .views import CustomLoginView
from .views import CustomLogoutView
from . import views

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path("signup/", views.signup, name="signup"),
]