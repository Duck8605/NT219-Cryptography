INSTALLED_APPS = [
    # ... existing apps
    'django_otp',
    'django_otp.plugins.otp_totp',  # Time-based OTP
    'auth_app',  # Your custom authentication app
]

MIDDLEWARE = [
    # ... existing middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',  # OTP middleware must be after AuthenticationMiddleware
    # ... other middleware
]

OTP_TOTP_ISSUER = 'UIT Security'
