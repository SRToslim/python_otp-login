import random

import requests
from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from helpbazar import settings
from userauth.models import User, Profile
from userauth.utils import get_client_ip, get_client_os_info, get_client_browser_info


def mobile_login(request):
    if request.user.is_authenticated:
        messages.success(request, f'Hey you are already Logged In')
        return HttpResponseRedirect(reverse('index'))
    else:
        if request.method == 'post' or request.method == 'POST':
            phone_number = request.POST.get('phone')
            otp = str(random.randint(1000, 9999))

            data = {
                'api_token': settings.SMS_API_TOKEN,
                'sid': settings.SMS_SID,
                'msisdn': phone_number,
                'sms': f'Your OTP is: {otp}',
                'csms_id': str(random.randint(10000000, 99999999))
            }

            response = requests.post(settings.SMS_URL, data=data)
            if response.status_code == 200:
                print(data, response)
                request.session['phone'] = phone_number
                request.session['otp'] = otp
                return HttpResponseRedirect(reverse_lazy('otp'))
            else:
                messages.error(request, 'Failed to send OTP via SMS. Please try again.')
                return False
        else:
            return render(request, 'auth/mobile.html')


def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        phone_number = request.session.get('phone')
        user = User.objects.filter(phone=phone_number).first()

        if user_otp == stored_otp:
            if user:
                user.last_ip = get_client_ip(request)
                user.client_os_info = get_client_os_info(request)
                user.client_browser_info = get_client_browser_info(request)
                user.is_online = True
                user.save()
                login(request, user)
                return HttpResponseRedirect(reverse_lazy('index'))
            else:
                user = User.objects.create(username=phone_number, phone=phone_number)
                user.is_active = True
                user.is_verify = True
                user.ip = get_client_ip(request)
                user.client_os_info = get_client_os_info(request)
                user.client_browser_info = get_client_browser_info(request)
                user.is_online = True
                user.save()
                Profile.objects.create(user=user)
                login(request, user)
                return HttpResponseRedirect(reverse_lazy('index'))
        else:
            messages.error(request, 'OTP not matched.')
            return redirect(request.META.get('HTTP_REFERER'))
    return render(request, 'auth/otp.html')


def password_otp(request):
    if request.user.is_authenticated:
        messages.success(request, f'Hey you are already Logged In')
        return HttpResponseRedirect(reverse('index'))
    else:
        if request.method == 'post' or request.method == 'POST':
            phone_number = request.POST.get('phone')
            user = User.objects.filter(phone=phone_number).first()
            if user:
                otp = str(random.randint(1000, 9999))

                data = {
                    'api_token': settings.SMS_API_TOKEN,
                    'sid': settings.SMS_SID,
                    'msisdn': phone_number,
                    'sms': f'Your OTP is: {otp}',
                    'csms_id': str(random.randint(10000000, 99999999))
                }

                response = requests.post(settings.SMS_URL, data=data)
                if response.status_code == 200:
                    print(data, response)
                    request.session['phone'] = phone_number
                    request.session['otp'] = otp
                    return HttpResponseRedirect(reverse_lazy('forget-password-otp'))
                else:
                    messages.error(request, 'Failed to send OTP via SMS. Please try again.')
                    return False
            else:
                messages.error(request, 'User Not Found')
                return redirect(request.META.get('HTTP_REFERER'))
        else:
            return render(request, 'auth/forgot-password-mobile.html')


def reset_password_otp_verify(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')

        if user_otp == stored_otp:
            return render(request, 'auth/reset-password.html')
        else:
            messages.error(request, 'OTP not matched.')
            return redirect(request.META.get('HTTP_REFERER'))
    return render(request, 'auth/forgot-password-mobile-otp.html')


def confirm_password_reset(request):
    phone_number = request.session.get('phone')
    user = User.objects.filter(phone=phone_number).first()
    if request.method == "POST":
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        if password == password1:
            if user.check_password(password):
                messages.error(request, f'New password is same as Old Password. Try new one.')
                return render(request, 'auth/forgot-password-mobile-otp.html', {'user': user})
            else:
                user.set_password(password)
                user.save()
                login(request, user)
                return redirect('index')
        else:
            messages.error(request, f'Password and Confirm Password dose not match.')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        return render(request, 'auth/reset-password.html', {'user': user})
