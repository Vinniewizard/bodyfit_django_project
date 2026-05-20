from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserRegistrationViewSet, basename='user-register')
router.register(r'profiles', views.UserProfileViewSet, basename='user-profile')
router.register(r'fashion-images', views.FashionImageViewSet, basename='fashion-image')
router.register(r'body-analyses', views.BodyAnalysisViewSet, basename='body-analysis')
router.register(r'analytics', views.AnalyticsViewSet, basename='analytics')
router.register(r'notifications', views.UserNotificationViewSet, basename='notification')
router.register(r'ai-models', views.AIModelViewSet, basename='ai-model')

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('gallery/', views.gallery, name='gallery'),
    path('results/', views.results, name='results'),
    path('api/', include(router.urls)),
    path('api/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/login/', views.CustomTokenObtainPairView.as_view(), name='api_login'),
    path('api/register/', views.UserRegistrationViewSet.as_view({'post': 'create'}), name='api_register'),
    path('api/token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
]
