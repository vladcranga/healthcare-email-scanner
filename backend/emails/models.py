from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Email(models.Model):
    class EmailStatus(models.TextChoices):
        SAFE = 'safe', _('Safe')
        SUSPICIOUS = 'suspicious', _('Suspicious')
        DANGEROUS = 'dangerous', _('Dangerous')

    sender = models.EmailField(_('Sender Email'))
    sender_name = models.CharField(_('Sender Name'), max_length=255, blank=True)
    subject = models.CharField(_('Subject'), max_length=512)
    content = models.TextField(_('Email Content'))
    received_date = models.DateTimeField(_('Received Date'), auto_now_add=True)
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=EmailStatus.choices,
        default=EmailStatus.SAFE
    )
    confidence_score = models.FloatField(_('ML Confidence Score'), default=0.0)
    is_quarantined = models.BooleanField(_('Is Quarantined'), default=False)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_emails'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_emails'
    )
    has_attachments = models.BooleanField(_('Has Attachments'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-received_date']
        verbose_name = _('Email')
        verbose_name_plural = _('Emails')

    def __str__(self):
        return f"{self.sender} - {self.subject} ({self.status})"


class EmailAttachment(models.Model):
    email = models.ForeignKey(
        Email,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(_('File'), upload_to='email_attachments/')
    filename = models.CharField(_('Original Filename'), max_length=255)
    content_type = models.CharField(_('Content Type'), max_length=100)
    size = models.IntegerField(_('File Size (bytes)'))
    is_suspicious = models.BooleanField(_('Is Suspicious'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Email Attachment')
        verbose_name_plural = _('Email Attachments')

    def __str__(self):
        return f"{self.filename} ({self.email.subject})"


class SuspiciousPattern(models.Model):
    pattern = models.CharField(_('Pattern'), max_length=255, unique=True)
    category = models.CharField(_('Category'), max_length=100)
    severity = models.IntegerField(_('Severity'), default=1)
    description = models.TextField(_('Description'), blank=True)
    is_regex = models.BooleanField(_('Is Regular Expression'), default=False)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Suspicious Pattern')
        verbose_name_plural = _('Suspicious Patterns')

    def __str__(self):
        return f"{self.pattern} ({self.category})"


class EmailAnalysis(models.Model):
    email = models.OneToOneField(
        Email,
        on_delete=models.CASCADE,
        related_name='analysis'
    )
    matched_patterns = models.ManyToManyField(SuspiciousPattern)
    ml_prediction = models.JSONField(_('ML Prediction Details'), default=dict)
    analysis_date = models.DateTimeField(auto_now_add=True)
    risk_score = models.FloatField(_('Risk Score'), default=0.0)
    notes = models.TextField(_('Analysis Notes'), blank=True)

    class Meta:
        verbose_name = _('Email Analysis')
        verbose_name_plural = _('Email Analyses')

    def __str__(self):
        return f"Analysis for {self.email.subject}"
