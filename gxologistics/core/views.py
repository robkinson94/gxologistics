from datetime import timedelta
import os
from decouple import config
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, Metric, Record, Team
from .serializers import MetricSerializer, RecordSerializer, TeamSerializer
from .utils import email_verification_token


class RegisterUserView(APIView):
    def post(self, request):
        """
        Handles user registration with detailed 400 error on password validation failure.
        """
        data = request.data
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        # Validate passwords match
        if password != confirm_password:
            return Response(
                {"password": ["Passwords do not match."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate password strength
        try:
            validate_password(password)
        except DjangoValidationError as e:
            # Format the error messages and return a 400 response
            return Response(
                {"password": e.messages}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if username or email is already taken
        if CustomUser.objects.filter(username=username).exists():
            return Response(
                {"username": ["This username is already taken."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if CustomUser.objects.filter(email=email).exists():
            return Response(
                {"email": ["This email is already registered."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_active = False
        user.save()

        # Generate email verification token
        token = email_verification_token.make_token(user)
        
        # Fetch React domain and paths from environment variables
        react_domain = os.environ.get("REACT_DOMAIN", "http://localhost:3000")
        react_verify_path = os.environ.get("REACT_VERIFY_PATH", "/verify")
        react_redirect_path = os.environ.get("REACT_REDIRECT_PATH", "/redirect")
        
        # Create verification link
        verification_link = f"{react_domain}{react_verify_path}?token={token}&uid={user.id}"
        
        # Send email
        send_mail(
            subject="Verify Your Email",
            message=f"Click the link to verify your email: {verification_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        
        # Generate redirect URL for JSON response
        react_redirect_url = f"{react_domain}{react_redirect_path}?token={token}&uid={user.id}"
        return JsonResponse(
            {"redirect_url": react_redirect_url}, status=status.HTTP_201_CREATED
        )


class VerifyEmailView(APIView):
    def post(self, request):
        token = request.data.get("token")
        uid = request.data.get("uid")

        user = get_object_or_404(CustomUser, id=uid)

        # Check if the token is valid
        if email_verification_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                {"message": "Email verified successfully!"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class IsCustomAdminUser(BasePermission):
    """
    Allows access only to users with is_admin=True.
    Superusers will not bypass this check.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class TeamCRUDView(APIView):

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "DELETE"]:
            self.permission_classes = [IsAuthenticated, IsCustomAdminUser]
        elif self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def post(self, request):
        """
        Create a new team.
        """
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                raise ValidationError({"name": "A team with this name already exists."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        """
        Retrieve a team or list all teams.
        """
        if pk:
            try:
                team = Team.objects.get(pk=pk)
            except Team.DoesNotExist:
                return Response(
                    {"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND
                )
            serializer = TeamSerializer(team)
            return Response(serializer.data, status=status.HTTP_200_OK)
        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update an existing team.
        """
        try:
            team = Team.objects.get(pk=pk)
        except Team.DoesNotExist:
            return Response(
                {"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = TeamSerializer(team, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a team.
        """
        try:
            team = Team.objects.get(pk=pk)
        except Team.DoesNotExist:
            return Response(
                {"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND
            )

        team.delete()
        return Response(
            {"message": "Team deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class MetricCRUDView(APIView):

    def get_permissions(self):
        """
        Dynamically assign permissions based on request method.
        """
        if self.request.method in ["POST", "PUT", "DELETE"]:
            self.permission_classes = [IsAuthenticated, IsCustomAdminUser]
        elif self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def post(self, request):
        """
        Create a new metric.
        """
        serializer = MetricSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                raise ValidationError(
                    {"name": "A metric with this name already exists."}
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        """
        Retrieve a metric or list all metrics.
        """
        if pk:
            metric = get_object_or_404(Metric, pk=pk)
            serializer = MetricSerializer(metric)
            return Response(serializer.data, status=status.HTTP_200_OK)
        metrics = Metric.objects.all()
        serializer = MetricSerializer(metrics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update an existing metric.
        """
        metric = get_object_or_404(Metric, pk=pk)
        serializer = MetricSerializer(metric, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a metric.
        """
        metric = get_object_or_404(Metric, pk=pk)
        metric.delete()
        return Response(
            {"message": "Metric deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class RecordCRUDView(APIView):

    def get_permissions(self):
        """
        Dynamically assign permissions based on request method.
        """
        if self.request.method in ["POST", "PUT", "DELETE"]:
            self.permission_classes = [IsAuthenticated, IsCustomAdminUser]
        elif self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def post(self, request):
        """
        Create a new record.
        """
        serializer = RecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        if pk:
            record = get_object_or_404(Record, pk=pk)
            serializer = RecordSerializer(record)
            return Response(serializer.data, status=status.HTTP_200_OK)

        queryset = Record.objects.all()
        team_id = request.query_params.get("team")
        metric_id = request.query_params.get("metric")

        if team_id:
            queryset = queryset.filter(team__id=team_id)
        if metric_id:
            queryset = queryset.filter(metric__id=metric_id)

        serializer = RecordSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Update an existing record.
        """
        record = get_object_or_404(Record, pk=pk)
        serializer = RecordSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a record.
        """
        record = get_object_or_404(Record, pk=pk)
        record.delete()
        return Response(
            {"message": "Record deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Stacked bar chart data
        metric_team_data = Record.objects.values("metric__name", "team__name").annotate(
            total_value=Sum("value")
        )

        # Pie chart: Proportion of records by team
        records_by_team = Record.objects.values("team__name").annotate(
            total_records=Count("id")
        )

        # Line chart: Trends over time
        record_trends = (
            Record.objects.values("timestamp")
            .annotate(total_value=Sum("value"))
            .order_by("timestamp")
        )

        # Area chart: Total contributions by team
        team_contributions = Record.objects.values("team__name").annotate(
            total_value=Sum("value")
        )

        return Response(
            {
                "metricTeamData": list(metric_team_data),
                "recordsByTeam": list(records_by_team),
                "recordTrends": list(record_trends),
                "teamContributions": list(team_contributions),
            }
        )
