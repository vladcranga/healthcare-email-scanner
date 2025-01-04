from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    class UserRole(models.TextChoices):
        ADMIN = "admin", _("Admin")
        STAFF = "staff", _("Staff")

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(
        _("Role"), max_length=20, choices=UserRole.choices, default=UserRole.STAFF
    )
    department = models.CharField(_("Department"), max_length=100, blank=True)
    phone_number = models.CharField(_("Phone Number"), max_length=20, blank=True)
    receive_notifications = models.BooleanField(
        _("Receive Notifications"), default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class LoginHistory(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="login_history"
    )
    login_datetime = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(_("IP Address"), null=True, blank=True)
    user_agent = models.CharField(_("User Agent"), max_length=512, blank=True)
    is_successful = models.BooleanField(_("Is Successful"), default=True)

    class Meta:
        verbose_name = _("Login History")
        verbose_name_plural = _("Login Histories")
        ordering = ["-login_datetime"]

    def __str__(self):
        status = "successful" if self.is_successful else "failed"
        return f"{self.user.username} - {status} login at {self.login_datetime}"
