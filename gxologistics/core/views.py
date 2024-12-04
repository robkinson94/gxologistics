from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Team, Metric, Record
from .serializers import TeamSerializer, MetricSerializer, RecordSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Team
from .serializers import TeamSerializer
from rest_framework.permissions import BasePermission
from .models import CustomUser
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import email_verification_token


class RegisterUserView(APIView):
    def post(self, request):
        """
        Handles user registration with detailed 400 error on password validation failure.
        """
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

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
            return Response({"password": e.messages}, status=status.HTTP_400_BAD_REQUEST)

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
        current_site = get_current_site(request)
        verification_link = f"http://{current_site.domain}{reverse('email-verify')}?token={token}&uid={user.id}"

        # Send email
        send_mail(
            subject="Verify Your Email",
            message=f"Click the link to verify your email: {verification_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return Response({"message": "User registered successfully! Please check your email to verify your account."}, status=status.HTTP_201_CREATED)
    

class VerifyEmailView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        uid = request.query_params.get('uid')

        user = get_object_or_404(CustomUser, id=uid)

        # Check if the token is valid
        if email_verification_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


class IsCustomAdminUser(BasePermission):
    """
    Allows access only to users with is_admin=True.
    Superusers will not bypass this check.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin
    

class TeamCRUDView(APIView):

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsCustomAdminUser]
        elif self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()



    def post(self, request):
        """
        Create a new team.
        """
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        """
        Retrieve a team or list all teams.
        """
        if pk:
            try:
                team = Team.objects.get(pk=pk)
            except Team.DoesNotExist:
                return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)
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
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)

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
            return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)

        team.delete()
        return Response({"message": "Team deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

class MetricCRUDView(APIView):

    def get_permissions(self):
        """
        Dynamically assign permissions based on request method.
        """
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsCustomAdminUser]
        elif self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def post(self, request):
        """
        Create a new metric.
        """
        serializer = MetricSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        return Response({"message": "Metric deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class RecordCRUDView(APIView):

    def get_permissions(self):
        """
        Dynamically assign permissions based on request method.
        """
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsCustomAdminUser]
        elif self.request.method == 'GET':
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
        """
        Retrieve a record or list all records.
        """
        if pk:
            record = get_object_or_404(Record, pk=pk)
            serializer = RecordSerializer(record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        records = Record.objects.all()
        serializer = RecordSerializer(records, many=True)
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
        return Response({"message": "Record deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


