from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

admin.site.site_header = 'MedWaste Admin'
admin.site.site_title = 'MedWaste Admin Portal'
admin.site.index_title = 'Управление системой учета медотходов'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/organizations/', include('apps.organizations.urls')),
    path('api/v1/batches/', include('apps.batches.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
]

# Keep admin static assets available in local/dev runs.
urlpatterns += staticfiles_urlpatterns()
