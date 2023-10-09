from django.urls import path

from .views import *

urlpatterns = [
    path('mobile/', mobile_login, name='mobile'),
    path('mobile/otp/', verify_otp, name='otp'),
    path('mobile/forget-password/', password_otp, name='forget-password'),
    path('mobile/forget-password/otp', reset_password_otp_verify, name='forget-password-otp'),
]
