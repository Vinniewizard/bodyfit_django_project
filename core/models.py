from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

class UserProfile(models.Model):
    """Extended user profile with body analysis data"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True, validators=[MinValueValidator(100), MaxValueValidator(250)])
    weight_kg = models.FloatField(null=True, blank=True, validators=[MinValueValidator(30), MaxValueValidator(300)])
    dark_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class FashionImage(models.Model):
    """Store fashion images for analysis"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fashion_images')
    image = models.ImageField(upload_to='fashion_images/%Y/%m/%d/')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    clothing_type = models.CharField(
        max_length=50,
        choices=[
            ('dress', 'Dress'),
            ('shirt', 'Shirt'),
            ('pants', 'Pants'),
            ('jacket', 'Jacket'),
            ('other', 'Other'),
        ],
        default='other'
    )
    color = models.CharField(max_length=100, blank=True)
    style = models.CharField(
        max_length=50,
        choices=[
            ('casual', 'Casual'),
            ('formal', 'Formal'),
            ('sporty', 'Sporty'),
            ('vintage', 'Vintage'),
            ('trendy', 'Trendy'),
        ],
        blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', '-uploaded_at']),
            models.Index(fields=['clothing_type']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class BodyAnalysis(models.Model):
    """Store body shape analysis results"""
    BODY_CHOICES = [
        ('Pear', 'Pear'),
        ('Apple', 'Apple'),
        ('Hourglass', 'Hourglass'),
        ('Rectangle', 'Rectangle'),
        ('Inverted Triangle', 'Inverted Triangle'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='body_analyses')
    image = models.ImageField(upload_to='body_analysis/%Y/%m/%d/', null=True, blank=True)
    bust = models.FloatField(validators=[MinValueValidator(50), MaxValueValidator(200)])
    waist = models.FloatField(validators=[MinValueValidator(40), MaxValueValidator(200)])
    hips = models.FloatField(validators=[MinValueValidator(50), MaxValueValidator(200)])
    body_shape = models.CharField(max_length=50, choices=BODY_CHOICES)
    recommendation = models.TextField()
    confidence_score = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    analyzed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['user', '-analyzed_at']),
            models.Index(fields=['body_shape']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.body_shape} ({self.confidence_score}%)"


class AIModel(models.Model):
    """Track AI models used for body shape detection"""
    name = models.CharField(max_length=200, unique=True)
    version = models.CharField(max_length=50)
    accuracy = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    model_file = models.FileField(upload_to='ai_models/', null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} v{self.version}"


class AnalyticsData(models.Model):
    """Store analytics data for dashboard"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField(auto_now_add=True)
    total_analyses = models.IntegerField(default=0)
    images_uploaded = models.IntegerField(default=0)
    body_shape_distribution = models.JSONField(default=dict, blank=True)
    average_confidence = models.FloatField(default=0.0)
    active_sessions = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class UserNotification(models.Model):
    """Store user notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('analysis', 'Analysis Complete'),
            ('upload', 'Upload Successful'),
            ('recommendation', 'New Recommendation'),
            ('system', 'System Message'),
        ],
        default='system'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"
