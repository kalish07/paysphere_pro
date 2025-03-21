from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from ..models.user_models import User
from ..serializers import UserSerializer, UserRegistrationSerializer,UserLoginSerializer
from ..permissions import IsHRAdmin, IsEmployeeOrReadOnly  

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users with Role-Based Access Control (RBAC)"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsHRAdmin]  # Default: HR/Admin access only

    def get_permissions(self):
        """Dynamic permission handling"""
        if self.action in ['update_profile', 'current_user']:   
            return [IsAuthenticated()]  
        elif self.action in ['create', 'delete_user', 'activate_user']:
            return [IsHRAdmin()]  
        return super().get_permissions()

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """Allow registration for new users with validation."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='login', permission_classes=[])
    def login(self, request):
        """User login with JWT authentication"""
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  

        user = serializer.validated_data["user"]  

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login successful",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='current')
    def current_user(self, request):
        """Get details of the currently logged-in user."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='get')
    def get_user(self, request, pk=None):
        """Retrieve user details by ID (Employee can view only their own details)"""
        try:
            user = self.get_object()
            if request.user.group == "Employee" and request.user.id != user.id:
                return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['put'], url_path='update-profile', permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Employees can update their own profile but cannot modify sensitive fields"""
        user = request.user 
        restricted_fields = ["group", "is_active", "created_at", "modified_at"]

        # Check if the request contains restricted fields
        if any(field in request.data for field in restricted_fields):
            return Response({"error": "You are not allowed to modify these fields."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='deactivate')
    def deactivate_user(self, request, pk=None):
        """Soft delete (deactivate) a user (Only HR/Admin)"""
        try:
            user = self.get_object()
            if not request.user.has_perm("paysphere_app.change_user"):
                return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            user.is_active = False  
            user.save()
            return Response({"message": "User deactivated successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'], url_path='activate')
    def activate_user(self, request, pk=None):
        """Activate a previously deactivated user (Only HR/Admin)"""
        try:
            user = self.get_object()
            if not request.user.has_perm("paysphere_app.change_user"):
                return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            user.is_active = True  
            user.save()
            return Response({"message": "User activated successfully"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


def home(request):
    """Simple home response"""
    return HttpResponse("Welcome to PaySphere!")