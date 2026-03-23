from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.audit.models import log

from .models import DriverProfile, Recycler, User
from .serializers import (
    CustomTokenObtainPairSerializer,
    DriverProfileSerializer,
    LogoutSerializer,
    ProcessorDriverCreateSerializer,
    RecyclerOptionSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log(user, 'register', 'user', str(user.id), after={'login': user.login, 'role': user.role})
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    serializer_class = LogoutSerializer

    def post(self, request):
        try:
            RefreshToken(request.data.get('refresh')).blacklist()
        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class RecyclerListView(generics.ListAPIView):
    serializer_class = RecyclerOptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Recycler.objects.select_related('user', 'user__organization').all().order_by('id')

        if user.role in {'ADMIN', 'INSPECTOR'} or user.is_superuser:
            return queryset

        if user.role == 'RECYCLER':
            if user.organization_id:
                return queryset.filter(user__organization_id=user.organization_id)
            return queryset.none()

        if user.role == 'MEDICAL':
            if user.recycler_profile_id:
                return queryset.filter(pk=user.recycler_profile_id)
            if user.organization_id:
                return queryset.filter(user__organization_id=user.organization_id)
            return queryset.none()

        return queryset.none()


class ProcessorDriverAccessMixin:
    @staticmethod
    def _is_admin(user: User) -> bool:
        return bool(user and (user.role == 'ADMIN' or user.is_superuser))

    def _resolve_recycler(self, request) -> Recycler:
        user = request.user
        if self._is_admin(user):
            recycler_id = (
                request.query_params.get('recycler_id')
                or request.data.get('recycler_id')
                or user.recycler_profile_id
            )
            if not recycler_id:
                raise ValidationError({'recycler_id': 'Укажите recycler_id для работы администратора.'})
            return get_object_or_404(Recycler, pk=recycler_id)

        if user.role != 'MEDICAL':
            raise PermissionDenied('Доступно только переработчику или администратору.')
        if not user.recycler_profile_id:
            raise ValidationError('Профиль переработчика не привязан к пользователю.')

        return user.recycler_profile


class ProcessorDriverListCreateView(ProcessorDriverAccessMixin, generics.GenericAPIView):
    serializer_class = DriverProfileSerializer

    def get(self, request):
        recycler = self._resolve_recycler(request)
        queryset = recycler.drivers.select_related('user').all().order_by('id')
        return Response(DriverProfileSerializer(queryset, many=True).data)

    def post(self, request):
        recycler = self._resolve_recycler(request)
        serializer = ProcessorDriverCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vehicle_number = serializer.validated_data['vehicle_number']
        full_name = serializer.validated_data.get('full_name')
        login_value = serializer.validated_data.get('login')
        password = serializer.validated_data.get('password')

        driver = DriverProfile.objects.create(vehicle_number=vehicle_number)

        created_user = None
        if login_value and full_name and password:
            organization_id = serializer.validated_data.get('organization')
            if request.user.role == 'MEDICAL':
                organization_id = request.user.organization_id

            try:
                created_user = User.objects.create_user(
                    login=login_value,
                    password=password,
                    full_name=full_name,
                    role='DRIVER',
                    organization_id=organization_id,
                    driver_profile=driver,
                )
            except IntegrityError as exc:
                driver.delete()
                raise ValidationError({'login': 'Пользователь с таким логином уже существует.'}) from exc

        recycler.drivers.add(driver)

        log(
            request.user,
            'processor_driver_created',
            'driver_profile',
            driver.id,
            after={
                'vehicle_number': driver.vehicle_number,
                'recycler_id': recycler.id,
                'driver_user_id': created_user.id if created_user else None,
            },
        )

        return Response(DriverProfileSerializer(driver).data, status=status.HTTP_201_CREATED)


class ProcessorDriverAssignView(ProcessorDriverAccessMixin, APIView):
    def post(self, request, driver_id: int):
        recycler = self._resolve_recycler(request)
        driver = get_object_or_404(DriverProfile.objects.select_related('user'), pk=driver_id)

        if request.user.role == 'MEDICAL' and driver.user_id and request.user.organization_id and driver.user.organization_id:
            if request.user.organization_id != driver.user.organization_id:
                raise PermissionDenied('Нельзя привязать водителя из другой организации.')

        recycler.drivers.add(driver)
        log(request.user, 'processor_driver_assigned', 'driver_profile', driver.id, after={'recycler_id': recycler.id})
        return Response({'detail': 'Водитель привязан.'})

    def delete(self, request, driver_id: int):
        recycler = self._resolve_recycler(request)
        driver = get_object_or_404(DriverProfile, pk=driver_id)

        recycler.drivers.remove(driver)
        log(request.user, 'processor_driver_unassigned', 'driver_profile', driver.id, after={'recycler_id': recycler.id})
        return Response(status=status.HTTP_204_NO_CONTENT)
