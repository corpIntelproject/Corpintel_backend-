import random
from django.core.mail import send_mail
from django.core.cache import cache  # <-- We import Django's cache
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serilaizers import CompanyRegistrationSerializer
from .models import CorpTenant, CorpUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterCompanyView(APIView):
    """Temporarily holds data in Cache and emails the OTP."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CompanyRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            # DO NOT SAVE TO DATABASE YET! 
            # We just extract the clean JSON data.
            validated_data = serializer.validated_data
            
            # 1. Generate a random 6-digit OTP
            otp_code = str(random.randint(100000, 999999))
            
            # 2. Save everything temporarily in the server's Cache (RAM)
            cache_key = f"registration_otp_{validated_data['admin_email']}"
            cache.set(cache_key, {
                "user_data": validated_data,
                "otp_code": otp_code
            }, timeout=900) # 900 seconds = Expires in 15 minutes
            
            # 3. Send the OTP Email
            send_mail(
                subject='Verify Your Corporate Account',
                message=f'Hello {validated_data["admin_name"]},\n\nYour code is: {otp_code}\n\nIt expires in 15 minutes.',
                from_email='no-reply@yourcompany.com',
                recipient_list=[validated_data['admin_email']],
                fail_silently=False,
            )
            
            return Response({"message": "OTP sent to email. Please verify to complete registration."}, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailOTPView(APIView):
    """Checks the Cache OTP and officially saves the user to the Database."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)
            
        # 1. Look for the temporary data in the Cache
        cache_key = f"registration_otp_{email}"
        cached_data = cache.get(cache_key)
        
        if not cached_data:
            return Response({"error": "OTP has expired or email is incorrect. Please register again."}, status=status.HTTP_400_BAD_REQUEST)
            
        # 2. Check if the OTP matches
        if cached_data['otp_code'] != otp:
            return Response({"error": "Invalid OTP code."}, status=status.HTTP_400_BAD_REQUEST)
            
        # 3. OTP MATCHES! Now we finally save everything permanently to PostgreSQL!
        user_data = cached_data['user_data']
        
        tenant = CorpTenant.objects.create(
            organization_name=user_data['company_name'],
            registration_number=user_data['registration_number'],
            company_website=user_data['company_website'],
            headquarters_location=user_data['headquarters_location'],
            industry_type=user_data['industry_type']
        )
        
        user = CorpUser.objects.create_user(
            username=user_data['admin_email'],
            email=user_data['admin_email'],
            password=user_data['admin_password'],
            first_name=user_data['admin_name'],
            tenant_profile=tenant,
            system_role=CorpUser.AccessRoles.COMPANY_ADMIN,
            is_email_verified=True
        )
        
        # Delete the cache so they can't reuse the OTP
        cache.delete(cache_key)
        
        return Response({
            "message": "Email verified! Company and Admin officially registered.",
            "company_name": tenant.organization_name
        }, status=status.HTTP_201_CREATED)


class CustomLoginView(APIView):
    """Official Custom Login API for the Flutter app."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # 1. Grab the exact words 'email' and 'password' from the Flutter JSON
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({"error": "Please provide both email and password."}, status=status.HTTP_400_BAD_REQUEST)
            
        # 2. Authenticate the user against the database
        user = authenticate(username=email, password=password)
        
        if not user:
            return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
            
        # 3. Security Check: Are they verified?
        if not getattr(user, 'is_email_verified', False):
            return Response({"error": "Please verify your email before logging in."}, status=status.HTTP_403_FORBIDDEN)
            

        refresh = RefreshToken.for_user(user)
        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_profile": {
                "name": user.first_name,
                "email": user.email,
                "role": user.system_role,
                "company_name": user.tenant_profile.organization_name if user.tenant_profile else None
            }
        }, status=status.HTTP_200_OK)