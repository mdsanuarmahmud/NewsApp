from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse  # Import reverse function
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string
# Create your views here.




def login(request):
    if request.user.is_authenticated:
        return redirect('news_generating')
    else:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            remember_me = request.POST.get('remember_me')
            # user = authenticate(username=username, password=password)
            user = authenticate(request, email=email, password=password)
            print(user)
            if user is not None:
                auth.login(request, user)
                if remember_me:
                    request.session.set_expiry(60 * 60 * 24 * 14)   # Set a longer session timeout (e.g., 2 weeks)
                else:
                    request.session.set_expiry(0)    
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('news_generating')
            else:
                messages.info(request, 'Invalid password or username')
                return redirect(request.get_full_path()) # Need to return current URL cause next URL and normal URL are different
        else:
            template = 'user/login.html'
            return render(request, template)
    


def logout(request):
    auth.logout(request)
    return redirect('/')



@login_required(login_url='login')
def profile(request):
    user_profile = AppUser.objects.get(email=request.user.email)
    if request.method == 'POST':
        profile_image = request.FILES.get('img_upload')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if first_name:
            user_profile.first_name = first_name
            user_profile.save()
        if last_name:
            user_profile.last_name = last_name
            user_profile.save()
        if email:
            user_profile.email = email
            user_profile.save()
        if password1 and password1 == password2:
            user_profile.set_password(password1)
            user_profile.save()
        if profile_image:
            user_profile.profile_image = profile_image
            user_profile.save()
        return redirect('profile')
    return render(request, 'user/profile/profile.html', {'user_profile': user_profile})