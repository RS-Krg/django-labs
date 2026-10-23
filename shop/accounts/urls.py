from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views
from .forms import LoginForm

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(authentication_form=LoginForm), name='login'),
    path('', include('django.contrib.auth.urls')),
]
