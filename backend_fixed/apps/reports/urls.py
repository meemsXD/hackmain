from django.urls import path
from .views import JournalListView, JournalExportView, AuditListView

urlpatterns = [
    path('journal', JournalListView.as_view(), name='journal'),
    path('journal/export', JournalExportView.as_view(), name='journal-export'),
    path('audit', AuditListView.as_view(), name='audit'),
]
