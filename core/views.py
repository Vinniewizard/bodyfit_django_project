from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.models import UserProfile, FashionImage, BodyAnalysis, AnalyticsData, UserNotification, AIModel
from core.serializers import (
    UserSerializer, UserProfileSerializer, FashionImageSerializer,
    BodyAnalysisSerializer, AnalyticsDataSerializer, UserNotificationSerializer,
    UserRegistrationSerializer, AIModelSerializer
)
from django.db import models
import numpy as np
from PIL import Image
import io


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer with additional user info"""
    def validate(self, attrs):
        login_value = attrs.get(self.username_field)
        if login_value and '@' in login_value:
            try:
                attrs[self.username_field] = User.objects.get(email__iexact=login_value).username
            except User.DoesNotExist:
                pass
        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view"""
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh view"""
    pass


class UserRegistrationViewSet(viewsets.ViewSet):
    """Handle user registration"""
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'detail': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ModelViewSet):
    """Manage user profiles"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        profile = request.user.profile
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def toggle_dark_mode(self, request):
        profile = request.user.profile
        profile.dark_mode = not profile.dark_mode
        profile.save()
        return Response({'dark_mode': profile.dark_mode})


class FashionImageViewSet(viewsets.ModelViewSet):
    """Manage fashion images"""
    queryset = FashionImage.objects.all()
    serializer_class = FashionImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    filterset_fields = ['clothing_type', 'style']
    search_fields = ['title', 'description', 'color']
    ordering_fields = ['uploaded_at', 'title']

    def get_queryset(self):
        return FashionImage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent fashion images"""
        images = self.get_queryset().order_by('-uploaded_at')[:10]
        serializer = self.get_serializer(images, many=True)
        return Response(serializer.data)


class BodyAnalysisViewSet(viewsets.ModelViewSet):
    """Manage body analysis data"""
    queryset = BodyAnalysis.objects.all()
    serializer_class = BodyAnalysisSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    filterset_fields = ['body_shape']
    ordering_fields = ['analyzed_at', 'confidence_score']

    def get_queryset(self):
        return BodyAnalysis.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def analyze_image(self, request):
        """Analyze uploaded image for body shape detection"""
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'error': 'Image file required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Convert image to numpy array
            image = Image.open(image_file)
            image_array = np.array(image)

            # Placeholder for AI model detection
            body_shape = self.detect_body_shape(image_array)
            confidence = np.random.uniform(75, 99)

            # Combine request data with AI generated results
            data = request.data.copy()
            data.update({
                'body_shape': body_shape,
                'recommendation': self.get_recommendation(body_shape),
                'confidence_score': confidence,
            })

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            # Save once with all context
            analysis = serializer.save(user=request.user, image=image_file)
            
            return Response(self.get_serializer(analysis).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def detect_body_shape(self, image_array):
        """Simple body shape detection"""
        body_shapes = ['Pear', 'Apple', 'Hourglass', 'Rectangle', 'Inverted Triangle']
        return np.random.choice(body_shapes)

    def get_recommendation(self, body_shape):
        """Get style recommendations based on body shape"""
        recommendations = {
            'Pear': 'We recommend A-line dresses that skim the hips and highlight your waist.',
            'Apple': 'Empire waist dresses are perfect for you as they draw attention to the narrowest part of your torso.',
            'Hourglass': 'Wrap dresses are your best friend, perfectly accentuating your balanced proportions.',
            'Rectangle': 'Try sheath dresses with a belt to create the illusion of curves.',
            'Inverted Triangle': 'Halter-neck or V-neck fit-and-flare dresses help balance broader shoulders.',
        }
        return recommendations.get(body_shape, 'Consider styles that complement your unique body shape.')

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of all analyses"""
        analyses = self.get_queryset()
        body_shape_counts = {}
        for analysis in analyses:
            shape = analysis.body_shape
            body_shape_counts[shape] = body_shape_counts.get(shape, 0) + 1

        avg_conf = analyses.aggregate(avg_confidence=models.Avg('confidence_score'))['avg_confidence'] or 0

        return Response({
            'total_analyses': analyses.count(),
            'average_confidence': avg_conf,
            'body_shape_distribution': body_shape_counts
        })


class AnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """View analytics data"""
    queryset = AnalyticsData.objects.all()
    serializer_class = AnalyticsDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AnalyticsData.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard analytics"""
        user = request.user
        today_analytics = AnalyticsData.objects.filter(user=user).first()

        return Response({
            'total_images': FashionImage.objects.filter(user=user).count(),
            'total_analyses': BodyAnalysis.objects.filter(user=user).count(),
            'today_analytics': AnalyticsDataSerializer(today_analytics).data if today_analytics else {},
        })


class UserNotificationViewSet(viewsets.ModelViewSet):
    """Manage user notifications"""
    queryset = UserNotification.objects.all()
    serializer_class = UserNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserNotification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().update(is_read=True)
        return Response({'detail': 'All notifications marked as read'})


class AIModelViewSet(viewsets.ReadOnlyModelViewSet):
    """View available AI models"""
    queryset = AIModel.objects.filter(is_active=True)
    serializer_class = AIModelSerializer
    permission_classes = [AllowAny]


def home(request):
    """Home page view"""
    return render(request, 'home.html')


def login_page(request):
    """Login page view"""
    return render(request, 'login.html')


def register_page(request):
    """Register page view"""
    return render(request, 'register.html')


def dashboard(request):
    """Dashboard page view"""
    return render(request, 'dashboard.html')


def gallery(request):
    """Gallery page view"""
    return render(request, 'gallery.html')


def results(request):
    """Results page view"""
    return render(request, 'results.html')
