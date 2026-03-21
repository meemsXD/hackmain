from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, LogoutView, MeView, ProfileUpdateView, SignatureSetupView, ChangePasswordView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('refresh', TokenRefreshView.as_view(), name='refresh'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('me', MeView.as_view(), name='me'),
    path('profile', ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/signature/setup', SignatureSetupView.as_view(), name='signature-setup'),
    path('profile/signature/rotate', SignatureSetupView.as_view(), name='signature-rotate'),
    path('profile/change-password', ChangePasswordView.as_view(), name='change-password'),
]
