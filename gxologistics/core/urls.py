from django.urls import path, include
from .views import TeamCRUDView, MetricCRUDView, RecordCRUDView, RegisterUserView, VerifyEmailView


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('teams/', TeamCRUDView.as_view(), name='team-list-create'),  # For list and create
    path('teams/<int:pk>/', TeamCRUDView.as_view(), name='team-detail-update-delete'),  # For detail, update, delete
    path('metrics/', MetricCRUDView.as_view(), name='metric-list-create'),
    path('metrics/<int:pk>/', MetricCRUDView.as_view(), name='metric-detail-update-delete'),
    path('records/', RecordCRUDView.as_view(), name='record-list-create'),
    path('records/<int:pk>/', RecordCRUDView.as_view(), name='record-detail-update-delete'),
    path('verify-email/', VerifyEmailView.as_view(), name='email-verify'),
]