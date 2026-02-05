from django.db import models
from django.contrib.auth.models import User
import secrets


class Clinic(models.Model):
    name = models.CharField(max_length=255)

    clinic_code = models.CharField(
        max_length=12,
        unique=True,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.clinic_code:
            self.clinic_code = secrets.token_hex(4)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="userprofile"
    )

    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name="users"
    )

    def __str__(self):
        return f"{self.user.username} - {self.clinic.name}"


class FollowUp(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('done', 'Done')
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi')
    ]

    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name="followups"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_followups"
    )

    patient_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)

    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES
    )

    notes = models.TextField(blank=True, null=True)

    due_date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    public_token = models.CharField(
        max_length=32,
        unique=True,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.public_token:
            while True:
                token = secrets.token_urlsafe(12)
                if not FollowUp.objects.filter(public_token=token).exists():
                    self.public_token = token
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_name} - {self.status}"


class PublicViewLog(models.Model):
    followup = models.ForeignKey(
        FollowUp,
        on_delete=models.CASCADE,
        related_name="views"
    )

    viewed_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"View of {self.followup.id} at {self.viewed_at}"
