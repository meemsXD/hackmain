from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    CustomTokenObtainPairSerializer, ProfileUpdateSerializer,
    SignatureSetupSerializer,
)
from apps.audits.services import audit_log

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        audit_log(user, 'user_registered', 'user', str(user.id), None, {'email': user.email})
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)

class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    def post(self, request):
        refresh = request.data.get('refresh')
        if refresh:
            try:
                token = RefreshToken(refresh)
                token.blacklist()
            except Exception:
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)

class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileUpdateSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        before = {'full_name': self.request.user.full_name, 'phone': self.request.user.phone}
        user = serializer.save()
        audit_log(user, 'profile_updated', 'user', str(user.id), before, {'full_name': user.full_name, 'phone': user.phone})

class SignatureSetupView(APIView):
    def post(self, request):
        serializer = SignatureSetupSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        audit_log(request.user, 'signature_setup', 'user', str(request.user.id), None, {'configured': True})
        return Response({'detail': 'Токен подписи сохранен'})

class ChangePasswordView(APIView):
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not request.user.check_password(old_password):
            return Response({'detail': 'Неверный текущий пароль'}, status=400)
        request.user.set_password(new_password)
        request.user.save(update_fields=['password', 'updated_at'])
        return Response({'detail': 'Пароль обновлен'})
