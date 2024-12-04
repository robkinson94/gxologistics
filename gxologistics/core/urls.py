from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamCRUDView, MetricViewSet, RecordViewSet, RegisterUserView, VerifyEmailView


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('teams/', TeamCRUDView.as_view(), name='team-list-create'),  # For list and create
    path('teams/<int:pk>/', TeamCRUDView.as_view(), name='team-detail-update-delete'),  # For detail, update, delete
    path('verify-email/', VerifyEmailView.as_view(), name='email-verify'),
]
