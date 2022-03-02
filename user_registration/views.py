import datetime
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from user_registration.models import User
from Crypto.PublicKey import ECC


def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect("/")


def get_random_username(length=10, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(random.choice(allowed_chars) for i in range(length))


def registration(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        adhar_card_number = request.POST.get('adhar_card_number')
        date_of_bitrh = request.POST.get('date_of_birth')
        city = request.POST.get('city')

        username = get_random_username()
        raw_password = User.objects.make_random_password(length=10)
        password = make_password(raw_password)

        user_obj = User.objects.create(username=username, password=password, first_name=first_name, last_name=last_name,
                                       email=user_email, phone_number=phone_number, city=city, address=address,
                                       adhar_card_no=adhar_card_number)
        dob = datetime.datetime.strptime(date_of_bitrh, "%Y-%m-%d").date()

        user_obj.date_of_birth = dob

        # TODO generate key pair
        key = ECC.generate(curve='P-256')
        private_key = key.export_key(format='PEM')

        public_key = key.public_key().export_key(format="PEM")

        user_obj.user_public_key = public_key  # TODO assign public key to user
        user_obj.save()

        subject = "BlockChain Voting credentials"
        message_body = """
        Dear {0} {1}, 
        
        Please find below login credential for voting,
        
        Username = {2},
        Password = {3},
        Private Key = 
        {4}
        
        Site URL = {5}
        
        Please use above Private key for voting.
        
        Thank you,
        BlockChain voting System
        """.format(first_name, last_name, username, raw_password, private_key, 'http://localhost:8000/')

        from_email = settings.EMAIL_HOST_USER
        to_email = [user_email]

        send_mail(
            subject,
            message_body,
            from_email,
            to_email,
        )

        return HttpResponse("Success")

    else:
        return render(request, 'registration.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('loginPassword')

        user = authenticate(username=username, password=password)  # authenticate the user
        if user:
            login(request, user)
        else:
            print("\n\nUser not authenticated...!")

        return render(request, 'home.html')
    else:
        if request.user.is_authenticated:
            return render(request, 'home.html')
        return render(request, 'login.html')


@transaction.atomic
def forgot_password_view(request):
    if request.method == 'GET':
        return render(request, 'forgot_password.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        usr_obj = User.objects.filter(username=username)
        if usr_obj.exists():
            usr_email = usr_obj[0].email
            raw_password = User.objects.make_random_password(length=10)
            subject = "BlockChain Voting credentials"
            message_body = """
                    Dear {0} {1}, 

                    Please find below login credential for voting,

                    Username = {2},
                    Password = {3},

                    Thank you,
                    BlockChain voting System
                    """.format(usr_obj[0].first_name, usr_obj[0].last_name, usr_obj[0].username, raw_password,
                               settings.SITE_URL)

            from_email = settings.EMAIL_HOST_USER
            to_email = [usr_email]
            try:
                send_mail(
                    subject,
                    message_body,
                    from_email,
                    to_email,
                )
            except Exception as e:
                messages.warning(request, f'Some error has been occurred, Please try again later.\n Error- {e}')
                return redirect('/')

            usr_obj.update(password=make_password(raw_password))

            messages.success(request,
                             'Your password has been sent to your registered email id, kindly check your email.')
            return redirect('/')
        else:
            messages.warning(request, 'Invalid Username')
            return redirect('/')
