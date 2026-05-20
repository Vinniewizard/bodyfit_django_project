from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from core.models import UserProfile, FashionImage, BodyAnalysis, AIModel, AnalyticsData, UserNotification


# Custom Admin Site
class BodyFitAdminSite(AdminSite):
    site_header = 'BodyFit Pro Administration'
    site_title = 'BodyFit Pro Admin'
    index_title = 'Welcome to BodyFit Pro Admin Panel'
    site_url = '/staff-admin/'


bodyfit_admin = BodyFitAdminSite(name='bodyfit_admin')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'height_cm', 'weight_kg', 'dark_mode', 'bmi_display', 'created_at']
    list_filter = ['dark_mode', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']
    readonly_fields = ['created_at', 'updated_at', 'bmi_display']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'bio', 'profile_picture')
        }),
        ('Body Measurements', {
            'fields': ('height_cm', 'weight_kg', 'bmi_display')
        }),
        ('Preferences', {
            'fields': ('dark_mode',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['enable_dark_mode', 'disable_dark_mode']

    def bmi_display(self, obj):
        if obj.height_cm and obj.weight_kg:
            height_m = obj.height_cm / 100
            bmi = obj.weight_kg / (height_m ** 2)
            color = 'green' if 18.5 <= bmi <= 24.9 else 'orange' if 25 <= bmi <= 29.9 else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f}</span>',
                color,
                bmi
            )
        return 'N/A'
    bmi_display.short_description = 'BMI'

    def enable_dark_mode(self, request, queryset):
        queryset.update(dark_mode=True)
        self.message_user(request, _('Dark mode enabled for selected users.'))
    enable_dark_mode.short_description = 'Enable dark mode for selected users'

    def disable_dark_mode(self, request, queryset):
        queryset.update(dark_mode=False)
        self.message_user(request, _('Dark mode disabled for selected users.'))
    disable_dark_mode.short_description = 'Disable dark mode for selected users'


@admin.register(FashionImage)
class FashionImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'clothing_type', 'style', 'color', 'uploaded_at', 'image_preview']
    list_filter = ['clothing_type', 'style', 'uploaded_at']
    search_fields = ['title', 'description', 'color', 'user__username']
    readonly_fields = ['uploaded_at', 'updated_at', 'image_preview', 'image_full']
    fieldsets = (
        ('Image Information', {
            'fields': ('title', 'description', 'image', 'image_preview', 'image_full')
        }),
        ('Classification', {
            'fields': ('clothing_type', 'color', 'style')
        }),
        ('User', {
            'fields': ('user',)
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_casual', 'mark_as_formal']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return 'No Image'
    image_preview.short_description = 'Preview'

    def image_full(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="400" style="max-width: 100%; border-radius: 5px;" />', obj.image.url)
        return 'No Image'
    image_full.short_description = 'Full Image'

    def mark_as_casual(self, request, queryset):
        queryset.update(style='casual')
        self.message_user(request, _('Selected images marked as casual.'))
    mark_as_casual.short_description = 'Mark selected as casual'

    def mark_as_formal(self, request, queryset):
        queryset.update(style='formal')
        self.message_user(request, _('Selected images marked as formal.'))
    mark_as_formal.short_description = 'Mark selected as formal'


@admin.register(BodyAnalysis)
class BodyAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'body_shape', 'confidence_score', 'analyzed_at', 'confidence_display', 'measurement_summary']
    list_filter = ['body_shape', 'analyzed_at']
    search_fields = ['user__username', 'recommendation']
    readonly_fields = ['analyzed_at', 'updated_at', 'confidence_display', 'measurement_summary']
    fieldsets = (
        ('Analysis Information', {
            'fields': ('user', 'body_shape', 'confidence_display', 'analyzed_at')
        }),
        ('Measurements', {
            'fields': ('bust', 'waist', 'hips', 'measurement_summary')
        }),
        ('Results', {
            'fields': ('recommendation', 'image')
        }),
        ('Timestamps', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    actions = ['high_confidence_analysis', 'low_confidence_analysis']

    def confidence_display(self, obj):
        color = 'green' if obj.confidence_score >= 80 else 'orange' if obj.confidence_score >= 60 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 1.1em;">{}%</span>',
            color,
            obj.confidence_score
        )
    confidence_display.short_description = 'Confidence Score'

    def measurement_summary(self, obj):
        return format_html(
            '<strong>B:</strong> {}cm | <strong>W:</strong> {}cm | <strong>H:</strong> {}cm',
            obj.bust, obj.waist, obj.hips
        )
    measurement_summary.short_description = 'Measurements'

    def high_confidence_analysis(self, request, queryset):
        count = queryset.filter(confidence_score__gte=80).count()
        self.message_user(request, _('{} analyses with high confidence (>=80%).').format(count))
    high_confidence_analysis.short_description = 'Show high confidence analyses'

    def low_confidence_analysis(self, request, queryset):
        count = queryset.filter(confidence_score__lt=60).count()
        self.message_user(request, _('{} analyses with low confidence (<60%).').format(count))
    low_confidence_analysis.short_description = 'Show low confidence analyses'


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'accuracy_display', 'is_active', 'created_at', 'status_badge']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'version']
    readonly_fields = ['created_at', 'updated_at', 'accuracy_display']
    fieldsets = (
        ('Model Information', {
            'fields': ('name', 'version', 'description')
        }),
        ('Performance', {
            'fields': ('accuracy', 'accuracy_display', 'is_active')
        }),
        ('Model File', {
            'fields': ('model_file',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['activate_models', 'deactivate_models']

    def accuracy_display(self, obj):
        color = 'green' if obj.accuracy >= 90 else 'orange' if obj.accuracy >= 70 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color,
            obj.accuracy
        )
    accuracy_display.short_description = 'Accuracy'

    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span class="badge bg-success">Active</span>')
        return format_html('<span class="badge bg-secondary">Inactive</span>')
    status_badge.short_description = 'Status'

    def activate_models(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, _('Selected models have been activated.'))
    activate_models.short_description = 'Activate selected models'

    def deactivate_models(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, _('Selected models have been deactivated.'))
    deactivate_models.short_description = 'Deactivate selected models'


@admin.register(AnalyticsData)
class AnalyticsDataAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'total_analyses', 'images_uploaded', 'average_confidence', 'activity_level']
    list_filter = ['date']
    search_fields = ['user__username']
    readonly_fields = ['date', 'activity_level']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'date')
        }),
        ('Activity Metrics', {
            'fields': ('total_analyses', 'images_uploaded', 'average_confidence', 'activity_level')
        }),
        ('Advanced Data', {
            'fields': ('body_shape_distribution', 'active_sessions'),
            'classes': ('collapse',)
        }),
    )

    def activity_level(self, obj):
        total = obj.total_analyses + obj.images_uploaded
        if total >= 10:
            return format_html('<span class="badge bg-success">High</span>')
        elif total >= 5:
            return format_html('<span class="badge bg-warning">Medium</span>')
        return format_html('<span class="badge bg-secondary">Low</span>')
    activity_level.short_description = 'Activity Level'


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at', 'status_badge']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'title', 'notification_type', 'is_read')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    actions = ['mark_as_read', 'mark_as_unread', 'send_analysis_notifications', 'send_upload_notifications']

    def status_badge(self, obj):
        if obj.is_read:
            return format_html('<span class="badge bg-secondary">Read</span>')
        return format_html('<span class="badge bg-primary">Unread</span>')
    status_badge.short_description = 'Status'

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, _('Selected notifications marked as read.'))
    mark_as_read.short_description = 'Mark selected as read'

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, _('Selected notifications marked as unread.'))
    mark_as_unread.short_description = 'Mark selected as unread'

    def send_analysis_notifications(self, request, queryset):
        count = queryset.filter(notification_type='analysis').count()
        self.message_user(request, _('{} analysis notifications selected.').format(count))
    send_analysis_notifications.short_description = 'Filter analysis notifications'

    def send_upload_notifications(self, request, queryset):
        count = queryset.filter(notification_type='upload').count()
        self.message_user(request, _('{} upload notifications selected.').format(count))
    send_upload_notifications.short_description = 'Filter upload notifications'


# Customize Admin Dashboard
from django.contrib.admin.models import LogEntry

LogEntry.objects.all()


class CustomAdminDashboard(admin.ModelAdmin):
    change_list_template = 'admin/custom_change_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['total_users'] = UserProfile.objects.count()
        extra_context['total_images'] = FashionImage.objects.count()
        extra_context['total_analyses'] = BodyAnalysis.objects.count()
        extra_context['active_users'] = UserProfile.objects.filter(user__is_active=True).count()
        return super().changelist_view(request, extra_context=extra_context)
