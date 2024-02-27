from datetime import datetime
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import *
from django.db import IntegrityError
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import custom_token_generator

from django.urls import reverse


# Create your views here.
def index(request):
    cars = Car.objects.filter(status='Accepted')
    return render(request, 'index.html',{'cars': cars})

def admin_log(request):
    return render(request,'admin-log.html') 

# def reg_customer(request):
#     return render(request,'customer-reg.html') 

def reg_dealer(request):
    if request.method == 'POST':
        a = request.POST.get('fname')
        b = request.POST.get('lname')
        c = request.POST.get('email')
        d = request.POST.get('pno')
        e = request.FILES.get('ad')
        f = request.POST.get('username')
        g = request.POST.get('password')
        
        if dealer.objects.filter(username=f).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'dealer-reg.html', {'messages': messages.get_messages(request)})
        else:
            try:
                data = dealer.objects.create(fname=a, lname=b, email=c, pno=d, ad=e, username=f)
                data1 = user.objects.create(username=f, password=g,status=1)
                messages.success(request, "Account created successfully!")
                print(messages.get_messages(request))
                return render(request, 'login.html', {'messages': messages.get_messages(request)})
            except IntegrityError:
                messages.error(request, 'Failed to create account.')
                print(messages.get_messages(request))
                return render(request, 'dealer-reg.html', {'messages': messages.get_messages(request)})
    else:
        return render(request, 'dealer-reg.html')
    

def reg_customer(request):
    if request.method == 'POST':
        a = request.POST.get('fname')
        b = request.POST.get('lname')
        c = request.POST.get('email')
        d = request.POST.get('pno')
        e = request.FILES.get('dl')
        f = request.POST.get('username')
        g = request.POST.get('password')
        
        if user.objects.filter(username=f).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'customer-reg.html', {'messages': messages.get_messages(request)})
        else:
            try:
                data = customer.objects.create(fname=a, lname=b, email=c, pno=d, dl=e, username=f)
                data1 = user.objects.create(username=f, password=g,status=2)
                messages.success(request, "Account created successfully!")
                print(messages.get_messages(request))
                return render(request, 'login.html', {'messages': messages.get_messages(request)})
            except IntegrityError:
                messages.error(request, 'Failed to create account.')
                print(messages.get_messages(request))
                return render(request, 'customer-reg.html', {'messages': messages.get_messages(request)})
    else:
        return render(request, 'customer-reg.html')


def profile(request):
    if 'username' in request.session:
        u = request.session['username']
        data = user.objects.get(username=u)
        if data.status == 0:
            cars = Car.objects.filter(status='Pending')
            ac_cars = Car.objects.filter(status='Accepted')
            bookings = Booking.objects.all()
            return render(request, 'admin-log.html', {'cars': cars, 'bookings': bookings, 'ac_cars': ac_cars})
        elif data.status == 1:
            cars = Car.objects.filter(username=u)
            bookings = Booking.objects.filter(car__username=u)
            return render(request, 'dealer-log.html', {'cars': cars,'bookings': bookings,'username': u})
        elif data.status == 2:
            cars = Car.objects.filter(status='Accepted')
            bookings = Booking.objects.filter(username=u)
            return render(request, 'customer-log.html', {'cars': cars,'bookings': bookings,'username': u})
    else:
        cars = Car.objects.filter(status='Accepted')
        return render(request, 'index.html',{'cars': cars})


def login(request):
    if request.method == 'POST':
        u = request.POST.get('user')
        p = request.POST.get('pass')
        try:
            data = user.objects.get(username=u)
            if data.password == p:
                request.session['username'] = u
                return redirect(profile)  
            else:
                messages.error(request, "Incorrect Password")
        except user.DoesNotExist:
            messages.error(request, "User does not exist")
    return render(request, 'login.html', {'messages': messages.get_messages(request)})

def logout(request):
    if 'username' in request.session:
        del request.session['username']  
        return render(request,'login.html')




def add_car(request):
    if request.method == 'POST':
        u = request.session.get('username')
        make = request.POST.get('make')
        model = request.POST.get('model')
        year = request.POST.get('year')
        regno = request.POST.get('regno')
        price = request.POST.get('price')
        rc = request.FILES.get('rc')
        photos = request.FILES.get('photos')
        
        try:
            car = Car.objects.create(username=u, make=make, model=model, year=year,regno=regno, price=price, rc=rc, photos=photos, status='Pending')
            messages.success(request, "Car added successfully!")
            return redirect(profile) 
        except IntegrityError:
            messages.error(request, 'Failed to add car.')
            return redirect(profile)
        
    username = request.session.get('username')
    cars = Car.objects.filter(username=username)
    return render(request, 'dealer-log.html', {'cars': cars})




def accept_car(request):
    if request.method == 'POST':
        car_id = request.POST.get('car_id')
        car = Car.objects.get(id=car_id)
        car.status = 'Accepted'
        car.save()
        messages.success(request, 'Car listing accepted successfully.')
    return redirect(profile)

def reject_car(request):
    if request.method == 'POST':
        car_id = request.POST.get('car_id')
        reason = request.POST.get('reason')
        car = Car.objects.get(id=car_id)
        car.status = 'Rejected'
        car.rejection_reason = reason
        car.save()
        messages.error(request, f'Car listing rejected. Reason: {reason}')
    return redirect(profile)



def book(request, regno):
    if request.method == 'POST':
        u = request.session.get('username')
        dropoff_location = request.POST.get('dropoff_location')
        dropoff_date_str = request.POST.get('dropoff_date')
        dropoff_time = request.POST.get('dropoff_time') 
        nod = request.POST.get('nod')  
        dropoff_date = datetime.strptime(dropoff_date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
        
        # Get the car object associated with the provided registration number
        car = Car.objects.get(regno=regno)
        cus = customer.objects.get(username=u)
        deal = dealer.objects.get(username=car.username)
        # Create a new booking object and assign the associated car
        data = Booking.objects.create(
            username=u,
            car=car,  # Assign the car object here
            regno=regno,
            dropoff_location=dropoff_location,
            dropoff_date=dropoff_date,
            dropoff_time=dropoff_time,
            nod=nod,
            customer=cus,
            dealer=deal
        )
        
        # Update the booked status of the car
        car.booked = True
        car.save()
        
        messages.success(request, 'Your trip request has been submitted successfully!')
        return redirect(profile) 
    return render(request, 'book.html', {'regno': regno})




def cancel_booking(request, booking_id):
        booking = Booking.objects.get(pk=booking_id)
        booking.car.booked = False
        booking.car.save()
        booking.delete()
        messages.success(request, "The booking was successfully canceled.")
        return redirect(profile) 


def delete_car(request, car_id):
    car = Car.objects.get(id=car_id)
    car.delete()
    messages.success(request,'Car deleted successfully.')
    return redirect(profile)



def about(request):
    return render(request,'about.html')

def services(request):
    return render(request,'services.html')

def pricing(request):
    return render(request,'pricing.html')

def car(request):
    cars = Car.objects.filter(status='Accepted')
    return render(request, 'car.html',{'cars': cars})

def blog(request):
    return render(request,'blog.html')

def contact(request):
    return render(request,'contact.html')



def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        u = None
        try:
            u = dealer.objects.get(email=email)
        except dealer.DoesNotExist:
            pass     
        if not u:  
            try:
                u= customer.objects.get(email=email)
            except customer.DoesNotExist:
                pass  
        
        if u:
            token = custom_token_generator.make_token(u)
            # Construct the password reset link
            uidb64 = urlsafe_base64_encode(force_bytes(u.email))
            reset_link = request.build_absolute_uri(f'/reset/{uidb64}/{token}/')
            subject = 'Password Reset Request'
            html_message = render_to_string('password_reset_email.html', {'reset_link': reset_link})
            # message = f'Please click the following link to reset your password: {reset_link}'
            send_mail(subject, '', 'rahulkmilan92@gmail.com', [email],html_message=html_message)
            messages.success(request, 'Password reset link sent to your email.')
            return redirect('password_reset_done')
        else:
            messages.error(request, 'User with this email does not exist.')
    return render(request, 'password_reset_form.html')



def password_reset_done(request):
    return render(request, 'password_reset_done.html')




def reset_link_expired(request):
    return render(request,'reset_link_expired.html')


def password_reset_confirm(request, uidb64, token):
    uid = urlsafe_base64_decode(uidb64).decode('utf-8')
    try:
        dealer_user = dealer.objects.get(email=uid)
    except (TypeError, ValueError, OverflowError, dealer.DoesNotExist):
        dealer_user = None

    try: 
        customer_user = customer.objects.get(email=uid)
    except (TypeError, ValueError, OverflowError, customer.DoesNotExist):
        customer_user = None

    if dealer_user is not None and custom_token_generator.check_token(dealer_user, token):
        User = dealer
        u = dealer_user
    elif customer_user is not None and custom_token_generator.check_token(customer_user, token):
        User = customer
        u = customer_user
    else:
        User = None
        u = None

    if User is not None and u is not None:
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            us=user.objects.get(username=u.username)
            us.password=new_password
            us.save()
            messages.success(request, 'Password has been reset successfully.')
            return redirect('login') 
        return render(request, 'password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
    else:
        return redirect('reset_link_expired')  

