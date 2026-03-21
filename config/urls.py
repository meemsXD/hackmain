from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/organizations/', include('apps.organizations.urls')),
    path('api/v1/role-requests/', include('apps.roles.urls')),
    path('api/v1/waste-types/', include('apps.directory.urls')),
    path('api/v1/educator/', include('apps.batches.urls_educator')),
    path('api/v1/driver/', include('apps.access.urls_driver')),
    path('api/v1/processor/', include('apps.batches.urls_processor')),
    path('api/v1/', include('apps.reports.urls')),
    path('api/v1/', include('apps.chat.urls')),
]
