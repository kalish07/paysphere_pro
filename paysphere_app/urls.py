from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, home

# Registering ViewSet with Router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', home, name='home'),  # Home route
    path('', include(router.urls)),  # Include all user routes from viewset
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Token Refresh
]