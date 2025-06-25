from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extended user profile model to store additional user information
    related to OTP authentication.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_enabled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
