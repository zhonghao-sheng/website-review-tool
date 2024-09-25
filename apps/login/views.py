from django.shortcuts import render, redirect
from django.http import HttpRequest
from login.models import User
from django.http import JsonResponse
from .forms import SignUpForm, VerifyUserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token, reset_password_token
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('search_link')  # Redirect to a suitable page after login
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')  # Redirect to a suitable page after logout

def check_login(request):
    if request.user.is_authenticated:
        return redirect('search_link')  # Redirect to the search page if logged in
    else:
        return redirect('login')  # Redirect to the login page if not logged in

def index(request):
    return render(request, 'index.html')

def activate(request, uidb64, token):
    model = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = model.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, f"Email has been confirmed. Now you can log into your account.")
        return redirect('login')
    else:
        messages.error(request, f"Link is invalid!")
    
    return redirect('index')

def activate_email(request, user, email):
    subject = "Activate your account."
    message = render_to_string("activate_email.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email_message = EmailMessage(subject, message, to=[email])
    if email_message.send():
        messages.success(request, f"Thank you {user} for signing up to the website review tool. Please check \
                         your email {email} inbox and click on the activation link to confirm registration.")
    else:
        messages.error(request, f"Problem sending email to {email}. Please ensure you have typed it correctly.")

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            user.is_active = False
            user.save()
            activate_email(request, user, form.cleaned_data.get('email'))
            return redirect('login')  # Redirect to login page after successful signup
        else:
            messages.error(request, mark_safe("".join([f"{msg}<br/>" for error_list in form.errors.as_data().values() for error in error_list for msg in error.messages])))
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def forgot_password(request):
    if request.method == 'POST':
        form = VerifyUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            user = authenticate(request, username=username, email=email)
            if user is not None:
                reset_password_email(request, user, email)
                return redirect('login')
            else:
                messages.error(request, f"No account found with the provided {username} and {email}.")
        else:
            messages.error(request, f"Username or password were invalid.")
    else:
        form = VerifyUserForm()
    return render(request, 'forgot_password.html', {'form': form})

def reset_password_email(request, user, email):
    subject = "Reset your password."
    message = render_to_string("reset_password_email.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': reset_password_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email_message = EmailMessage(subject, message, to=[email])
    if email_message.send():
        messages.success(request, f"An email has been sent to {email}. Please check your inbox or spam.")
    else:
        messages.error(request, f"Problem sending email to {email}. Please ensure you have typed it correctly.")

def reset_password(request, uidb64, token):
    model = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = model.objects.get(pk=uid)
    except:
        user = None

    if user is not None and reset_password_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, f"Email has been confirmed. Now you can log into your account.")
        return redirect('login')
    else:
        messages.error(request, f"Link is invalid!")
    
    return redirect('index')
