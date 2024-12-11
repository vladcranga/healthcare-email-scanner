from rest_framework import serializers
from .models import Email, EmailAttachment, SuspiciousPattern, EmailAnalysis
from django.contrib.auth.models import User


class EmailAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAttachment
        fields = ['id', 'filename', 'content_type', 'size', 'is_suspicious', 'created_at']


class SuspiciousPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspiciousPattern
        fields = ['id', 'pattern', 'category', 'severity', 'description', 'is_regex', 'is_active']


class EmailAnalysisSerializer(serializers.ModelSerializer):
    matched_patterns = SuspiciousPatternSerializer(many=True, read_only=True)

    class Meta:
        model = EmailAnalysis
        fields = ['id', 'matched_patterns', 'ml_prediction', 'analysis_date', 'risk_score', 'notes']


class EmailSerializer(serializers.ModelSerializer):
    attachments = EmailAttachmentSerializer(many=True, read_only=True)
    analysis = EmailAnalysisSerializer(read_only=True)
    reviewed_by = serializers.StringRelatedField(read_only=True)
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Email
        fields = [
            'id', 'sender', 'sender_name', 'subject', 'content',
            'received_date', 'status', 'confidence_score', 'is_quarantined',
            'reviewed_by', 'assigned_to', 'has_attachments', 'attachments',
            'analysis', 'created_at', 'updated_at'
        ]
        read_only_fields = ['reviewed_by']


class EmailListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    class Meta:
        model = Email
        fields = [
            'id', 'sender', 'sender_name', 'subject', 'received_date',
            'status', 'is_quarantined', 'has_attachments'
        ]
