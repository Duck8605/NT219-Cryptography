from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django_otp.decorators import otp_required
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
import qrcode
from io import BytesIO
import base64
from .models import UserProfile

def home(request):
    """Home page view"""
    return render(request, 'auth_app/home.html')

def login_view(request):
    """
    Custom login view that handles both password authentication
    and OTP verification if enabled for the user.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if user has OTP enabled
                try:
                    profile = UserProfile.objects.get(user=user)
                    if profile.otp_enabled:
                        # Store user ID in session for OTP verification
                        request.session['user_id_for_otp'] = user.id
                        return redirect('verify_otp')
                    else:
                        # No OTP required, proceed with login
                        login(request, user)
                        messages.success(request, f"Welcome, {username}!")
                        return redirect('dashboard')
                except UserProfile.DoesNotExist:
                    # Create profile if it doesn't exist
                    UserProfile.objects.create(user=user)
                    login(request, user)
                    messages.success(request, f"Welcome, {username}!")
                    return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'auth_app/login.html', {'form': form})

@login_required
def dashboard(request):
    """
    User dashboard view, requires login.
    If OTP is enabled, it also requires OTP verification.
    """
    # Check if user has OTP enabled
    try:
        profile = UserProfile.objects.get(user=request.user)
        otp_enabled = profile.otp_enabled
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
        otp_enabled = False
    
    # Get user's TOTP devices
    devices = TOTPDevice.objects.filter(user=request.user, confirmed=True)
    
    return render(request, 'auth_app/dashboard.html', {
        'otp_enabled': otp_enabled,
        'devices': devices
    })

@login_required
def setup_otp(request):
    """
    View for setting up OTP authentication.
    Generates a new TOTP device and QR code for the user.
    """
    # Check if user already has OTP enabled
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Create a new TOTP device
    device = TOTPDevice.objects.create(
        user=request.user,
        name=f"{request.user.username}'s device",
        confirmed=False
    )
    
    # Generate a random key for the device
    device.key = random_hex()
    device.save()
    
    # Generate QR code for the device
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Create the OTP URI
    provisioning_uri = device.config_url
    
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'auth_app/setup_otp.html', {
        'device': device,
        'qr_code': img_str,
        'secret_key': device.key,
    })

def verify_otp(request):
    """
    View for verifying OTP during login or when setting up a new device.
    """
    if request.method == 'POST':
        otp_token = request.POST.get('otp_token')
        
        # Check if this is part of the login flow
        if 'user_id_for_otp' in request.session:
            from django.contrib.auth.models import User
            user_id = request.session['user_id_for_otp']
            user = User.objects.get(id=user_id)
            
            # Verify the OTP token
            from django_otp import verify_token
            
            for device in TOTPDevice.objects.filter(user=user, confirmed=True):
                if device.verify_token(otp_token):
                    # OTP verified, log in the user
                    login(request, user)
                    # Clean up the session
                    del request.session['user_id_for_otp']
                    messages.success(request, "OTP verified successfully!")
                    return redirect('dashboard')
            
            messages.error(request, "Invalid OTP token.")
            return render(request, 'auth_app/verify_otp.html')
        
        # Check if this is part of the setup flow
        elif request.user.is_authenticated:
            # Get the most recent unconfirmed device
            device = TOTPDevice.objects.filter(
                user=request.user, 
                confirmed=False
            ).order_by('-id').first()
            
            if device and device.verify_token(otp_token):
                # OTP verified, confirm the device
                device.confirmed = True
                device.save()
                
                # Enable OTP for the user
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                profile.otp_enabled = True
                profile.save()
                
                messages.success(request, "OTP setup completed successfully!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid OTP token.")
    
    return render(request, 'auth_app/verify_otp.html')
