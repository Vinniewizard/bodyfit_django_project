from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import UserProfile, FashionImage, BodyAnalysis, AnalyticsData, UserNotification, AIModel


class UserSerializer(serializers.ModelSerializer):
    """Serialize user information"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serialize user profile with extended information"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'profile_picture', 'height_cm', 'weight_kg', 'dark_mode', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FashionImageSerializer(serializers.ModelSerializer):
    """Serialize fashion images"""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FashionImage
        fields = ['id', 'user', 'image', 'title', 'description', 'clothing_type', 'color', 'style', 'uploaded_at', 'updated_at']
        read_only_fields = ['id', 'user', 'uploaded_at', 'updated_at']


class BodyAnalysisSerializer(serializers.ModelSerializer):
    """Serialize body analysis data"""
    user = serializers.StringRelatedField(read_only=True)
    recommended_dresses = serializers.SerializerMethodField()

    class Meta:
        model = BodyAnalysis
        fields = [
            'id', 'user', 'image', 'bust', 'waist', 'hips', 'body_shape', 
            'recommendation', 'recommended_dresses', 'confidence_score', 
            'analyzed_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'analyzed_at', 'updated_at']

    def get_recommended_dresses(self, obj):
        """Find existing dress images that match the recommendation style"""
        # This filters existing FashionImage objects that are dresses
        # In a real scenario, this could be linked to a product catalog
        dresses = FashionImage.objects.filter(
            clothing_type='dress',
            user=obj.user
        )[:4]
        return FashionImageSerializer(dresses, many=True).data


class AIModelSerializer(serializers.ModelSerializer):
    """Serialize AI model information"""
    class Meta:
        model = AIModel
        fields = ['id', 'name', 'version', 'accuracy', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AnalyticsDataSerializer(serializers.ModelSerializer):
    """Serialize analytics data"""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AnalyticsData
        fields = ['id', 'user', 'date', 'total_analyses', 'images_uploaded', 'body_shape_distribution', 'average_confidence', 'active_sessions']
        read_only_fields = ['id', 'user', 'date']


class UserNotificationSerializer(serializers.ModelSerializer):
    """Serialize user notifications"""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserNotification
        fields = ['id', 'user', 'title', 'message', 'notification_type', 'is_read', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serialize user registration"""
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data.pop('password2'):
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
