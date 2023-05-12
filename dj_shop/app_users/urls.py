from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .views import (
    RegisterView,
    ProfileView,
    AddBalanceView,
    MyLoginView,
    MyLogoutView,
    StatusInfoView,
)


app_name = 'app_users'

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('add_balance/<int:pk>/', AddBalanceView.as_view(), name='add_balance'),
    path('status-info/<int:pk>/', StatusInfoView.as_view(), name='status_info')
]
