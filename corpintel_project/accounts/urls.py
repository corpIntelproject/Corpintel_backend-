from django.urls import path 
from .views import RegisterCompanyView,VerifyEmailOTPView,CustomLoginView
urlpatterns = [
    path('register/', RegisterCompanyView.as_view(), name='register_company'),
    path('verify-otp/', VerifyEmailOTPView.as_view(), name='verify_otp'),
    path('login/', CustomLoginView.as_view(), name='custom_login'),
    
]
