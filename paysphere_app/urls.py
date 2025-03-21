from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views.user_views import UserViewSet, home
from .views.leave_views import LeaveRequestViewSet 


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'leaves', LeaveRequestViewSet, basename='leave')  

urlpatterns = [
    path('', home, name='home'),
    path('', include(router.urls)), 
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]