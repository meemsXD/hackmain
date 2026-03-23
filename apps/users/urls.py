from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
    RecyclerListView,
    ProcessorDriverListCreateView,
    ProcessorDriverAssignView,
)

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('refresh', TokenRefreshView.as_view(), name='refresh'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('me', MeView.as_view(), name='me'),
    path('recyclers', RecyclerListView.as_view(), name='recyclers'),
    path('processor/drivers', ProcessorDriverListCreateView.as_view(), name='processor-drivers'),
    path('processor/drivers/<int:driver_id>/assign', ProcessorDriverAssignView.as_view(), name='processor-driver-assign'),
]
