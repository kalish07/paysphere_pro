from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, home


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', home, name='home'),  
    path('', include(router.urls)),  
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  
]