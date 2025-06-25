# Django Authentication with Password and OTP - Setup and Usage Guide

This guide explains how to set up and use the Django authentication system with password and One-Time Password (OTP) functionality.

## Prerequisites

- Python 3.6+
- Django 3.2+
- django-otp package
- qrcode package

## Installation

1. Install required packages:

```bash
pip install django django-otp qrcode pillow
```

2. Create a new Django project or use an existing one.

3. Add the following apps to your `INSTALLED_APPS` in settings.py:

```python
INSTALLED_APPS = [
    # ... existing apps
    'django_otp',
    'django_otp.plugins.otp_totp',  # Time-based OTP
    'auth_app',  # Your custom authentication app
]
```

4. Add the OTP middleware to your `MIDDLEWARE` in settings.py:

```python
MIDDLEWARE = [
    # ... existing middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',  # OTP middleware must be after AuthenticationMiddleware
    # ... other middleware
]
```

5. Configure OTP settings in settings.py:

```python
# OTP settings
OTP_TOTP_ISSUER = 'YourAppName'
```

6. Copy the provided files to your project:
   - models.py
   - views.py
   - urls.py
   - templates/auth_app/*.html

7. Include the auth_app URLs in your project's main urls.py:

```python
urlpatterns = [
    # ... other URL patterns
    path('', include('auth_app.urls')),
]
```

8. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

9. Create a superuser:

```bash
python manage.py createsuperuser
```

10. Run the development server:

```bash
python manage.py runserver
```

## Usage

### Password Authentication

1. Navigate to the login page at `/login/`
2. Enter your username and password
3. If OTP is not enabled, you'll be redirected to the dashboard
4. If OTP is enabled, you'll be redirected to the OTP verification page

### Setting Up OTP

1. Log in with your username and password
2. From the dashboard, click "Set up Two-Factor Authentication"
3. Scan the QR code with an authenticator app (Google Authenticator, Authy, etc.)
4. Enter the 6-digit code from your authenticator app
5. OTP will be enabled for your account

### Verifying OTP

1. When logging in with OTP enabled, you'll be redirected to the OTP verification page
2. Enter the 6-digit code from your authenticator app
3. If the code is valid, you'll be logged in and redirected to the dashboard

## Security Features

- Password validation with Django's built-in validators
- Time-based One-Time Password (TOTP) for two-factor authentication
- QR code generation for easy OTP setup
- Secure session handling for OTP verification flow

## Code Structure

- **models.py**: Contains the UserProfile model that extends Django's User model
- **views.py**: Contains views for login, dashboard, OTP setup, and OTP verification
- **urls.py**: URL configuration for the authentication app
- **templates/**: HTML templates for the authentication app

## Customization

You can customize the following aspects:

- OTP issuer name in settings.py
- Password validation rules in settings.py
- HTML templates for login, dashboard, OTP setup, and OTP verification
- CSS styles in the HTML templates

## Production Considerations

For production deployment:

1. Change the SECRET_KEY in settings.py
2. Set DEBUG = False in settings.py
3. Configure a proper database (PostgreSQL, MySQL, etc.)
4. Use HTTPS to secure the authentication process
5. Consider using a more secure session backend
6. Implement rate limiting for login and OTP verification attempts
