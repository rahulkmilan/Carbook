from datetime import datetime, timezone
from django.core.mail import EmailMessage
import os
import re
import time
from datetime import timedelta
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
import razorpay
from .models import *
from django.db import IntegrityError
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import custom_token_generator
from django.views.decorators.csrf import csrf_exempt

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
        phone_regex = r'^\d{10}$'
        if not re.match(phone_regex, d):
            messages.error(request, "Please enter a valid 10-digit phone number.")
            return render(request, 'dealer-reg.html', {'messages': messages.get_messages(request)})
        
        if dealer.objects.filter(username=f).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'dealer-reg.html', {'messages': messages.get_messages(request)})
        elif customer.objects.filter(email=c).exists() or dealer.objects.filter(email=c).exists():
            messages.error(request, "This e-mail is already in use. Please use another e-mail")
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
        phone_regex = r'^\d{10}$'
        if not re.match(phone_regex, d):
            messages.error(request, "Please enter a valid 10-digit phone number.")
            return render(request, 'customer-reg.html', {'messages': messages.get_messages(request)})
        
        if user.objects.filter(username=f).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'customer-reg.html', {'messages': messages.get_messages(request)})
        elif customer.objects.filter(email=c).exists() or dealer.objects.filter(email=c).exists():
            messages.error(request, "This e-mail is already in use. Please use another e-mail")
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
            dealers = dealer.objects.all()
            customers = customer.objects.all()
            return render(request, 'admin-log.html', {'cars': cars, 'bookings': bookings, 'ac_cars': ac_cars,'dealers':dealers,'customers':customers})
        elif data.status == 1:
            cars = Car.objects.filter(username=u)
            bookings = Booking.objects.filter(car__username=u)
            today = datetime.now().date()
            for booking in bookings:
                booking.is_available = booking.dropoff_date + timedelta(days=booking.nod) >= today and booking.car.booked
            return render(request, 'dealer-log.html', {'cars': cars,'bookings': bookings,'username': u,'today':today})
        elif data.status == 2:
            # cars = Car.objects.filter(status='Accepted')
            # bookings = Booking.objects.filter(username=u)
            locations = Car.objects.order_by().values_list('location', flat=True).distinct()
            location = request.GET.get('location')
            if location:
                cars = Car.objects.filter(location=location, status='Accepted',booked=False)
            else:
                cars = Car.objects.filter(status='Accepted')
            bookings = Booking.objects.filter(username=u)
            today = datetime.now().date()
            for booking in bookings:
                if not booking.paid:
                    booking.delete()
                booking.cancel = booking.dropoff_date - timedelta(days=1) >= today and booking.car.booked
            return render(request, 'customer-log.html', {'cars': cars,'bookings': bookings,'username': u, 'locations': locations,'today':today})
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
        location = request.POST.get('location')
        price = request.POST.get('price')
        rc = request.FILES.get('rc')
        photos = request.FILES.get('photos')
        if Car.objects.filter(regno=regno).exists():
                messages.error(request, "Reg no. already exists. Re-check the regno.")
                return redirect(profile)
        try:
            car = Car.objects.create(username=u, make=make, model=model, year=year,regno=regno,location=location, price=price, rc=rc, photos=photos, status='Pending')
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
        deal = dealer.objects.get(username=car.username)

        messages.success(request, f'Car rejected due to {reason}.')
        # Sending email notification
        subject = f'Car Rejection: {car.make} {car.model}'
        message = f"Dear {deal.fname} {deal.lname}, your car ({car.regno} {car.make} {car.model}) has been rejected due to: {reason}."
        recipient_email = deal.email  # Assuming Car model has owner field with email
        sender_email = settings.EMAIL_HOST_USER  # Sender's email from settings
        send_mail(subject, message, sender_email, [recipient_email])
        car.delete()

    return redirect(profile)



def delete_car(request, car_id):
    car = Car.objects.get(id=car_id)
    car.delete()
    messages.success(request,'Car deleted successfully.')
    return redirect(profile)


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
            send_mail(subject, '', 'carbook.demo@gmail.com', [email],html_message=html_message)
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
            new_password_confirm = request.POST.get('new_password_confirm')
            if new_password_confirm == new_password:
                us=user.objects.get(username=u.username)
                us.password=new_password
                us.save()
                messages.success(request, 'Password has been reset successfully.')
                return redirect('login') 
            else:
                messages.error(request, "Passwords do not match.Try again")
        return render(request, 'password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
    else:
        return redirect('reset_link_expired')  



def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        try:
            send_mail(
                subject,
                f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}',
                email,  #sender email
                ['carbook.demo@gmail.com'],  #receiver email
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully.') 
            return redirect('login')  
        except IntegrityError:
            messages.error(request, 'Failed to sent.')
    return render(request,'contact.html')




def book(request, regno):
    prefill_data = {}
    amount = 0 
    context={}
    if request.method == 'POST':
        u = request.session.get('username')
        dropoff_location = request.POST.get('dropoff_location')
        dropoff_date_str = request.POST.get('dropoff_date')
        dropoff_time = request.POST.get('time') 
        nod = request.POST.get('nod') 
        dropoff_date = datetime.strptime(dropoff_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        
        # Get the car object associated with the provided registration number
        try:
            car = Car.objects.get(regno=regno)
            cus = customer.objects.get(username=u)
            deal = dealer.objects.get(username=car.username)
            
            # Calculate the amount
            amount = int(nod) * car.price 
            client = razorpay.Client(auth=("rzp_test_xJQ8e3ZkXc1mCY", "XOBYZLb5dTWcLjd4UcqEmNTw"))
                
            # Create Razorpay order
            order_data = {
                'amount': amount * 100,  
                'currency': 'INR',
                'receipt': 'order_rcptid_11',
                'payment_capture': 1
            }
            order = client.order.create(data=order_data)
            
            order_id = order['id']
            order_status = order['status']
            # Construct prefill data
            if cus:
                prefill_data = {
                    'name': f"{cus.fname} {cus.lname}",
                    'email': cus.email,
                    'contact': cus.pno,
                }
            data = Booking.objects.create(
            username=u,
            car=car,  # Assign the car object here
            regno=regno,
            dropoff_location=dropoff_location,
            dropoff_date=dropoff_date,
            dropoff_time=dropoff_time,
            nod=nod,
            customer=cus,
            dealer=deal,
            amount=amount,
            order_id=order_id
            )
        
        # Update the booked status of the car
            
            car.save()
            # client = razorpay.Client(auth=("rzp_test_xJQ8e3ZkXc1mCY", "XOBYZLb5dTWcLjd4UcqEmNTw"))
                
            # # Create Razorpay order
            # order_data = {
            #     'amount': amount,  
            #     'currency': 'INR',
            #     'receipt': 'order_rcptid_11',
            #     'payment_capture': 1
            # }
            # order = client.order.create(data=order_data)
            # print(order)  # Check if order creation is successful
            

            # order_id = order['id']
            # order_status = order['status']
            # # Construct prefill data
            # if cus:
            #     prefill_data = {
            #         'name': f"{cus.fname} {cus.lname}",
            #         'email': cus.email,
            #         'contact': cus.pno,
            #     }
            # Other logic for Razorpay payment creation
            
        except Car.DoesNotExist:
            return render(request, 'error.html', {'error': 'Car not found.'})
        except customer.DoesNotExist:
            return render(request, 'error.html', {'error': 'Customer not found.'})
        except dealer.DoesNotExist:
            return render(request, 'error.html', {'error': 'Dealer not found.'})
        except Exception as e:
            return render(request, 'error.html', {'error': str(e)})
        
        callback_url = 'http://127.0.0.1:8000'
        context = {
            'regno': regno,
            'prefill_data': prefill_data,
            'amount': amount,
            'order_id': order_id,
            'callback_url': callback_url,
            'data':data
        }
        return render(request, 'payment.html', context)
    return render(request, 'book.html',  {'regno': regno})



@csrf_exempt
def payment(request):
    if request.method == 'POST':
        response = request.POST
        params_dict = {
            'razorpay_order_id': response.get('razorpay_order_id', ''),
            'razorpay_payment_id': response.get('razorpay_payment_id', ''),
            'razorpay_signature': response.get('razorpay_signature', '')
        }
        client = razorpay.Client(auth=("rzp_test_xJQ8e3ZkXc1mCY", "XOBYZLb5dTWcLjd4UcqEmNTw"))
        order_id = params_dict['razorpay_order_id']
        razorpay_payment_id = params_dict['razorpay_payment_id']
        booking = Booking.objects.get(order_id=order_id)


        try:
            # Verify payment signature using Razorpay client
            status = client.utility.verify_payment_signature(params_dict)

            
            # Additional signature verification
            
            # secret = "XOBYZLb5dTWcLjd4UcqEmNTw"
            # generated_signature = hmac.new(
            #     secret.encode('utf-8'),
            #     f"{order_id}|{razorpay_payment_id}".encode('utf-8'),
            #     hashlib.sha256
            # ).hexdigest()
            
            # if generated_signature == params_dict['razorpay_signature']:
                # Signature verification successful
                # Payment is successful, update booking status or perform other actions
            if status:    
                booking.razorpay_payment_id = razorpay_payment_id
                booking.car.booked = True
                booking.car.save()
                booking.paid = True
                booking.save()

                subject = f'Car Booked'
                message = f"""Dear {booking.dealer.fname} {booking.dealer.lname}, 
                Your car ({booking.car.regno} {booking.car.make} {booking.car.model}) has been booked by {booking.customer.fname} {booking.customer.lname}.
                
                Booking details:
                Username: {booking.customer.username}
                Phone number: {booking.customer.pno}
                Email: {booking.customer.email}
                Dropoff date: {booking.dropoff_date}
                Dropoff time: {booking.dropoff_time}
                Dropoff location: {booking.dropoff_location}
                No. of days: {booking.nod}"""
                recipient_email = booking.dealer.email  
                sender_email = settings.EMAIL_HOST_USER  
                # send_mail(subject, message, sender_email, [recipient_email])
                email = EmailMessage(subject, message, sender_email, [recipient_email])
                dl_file = booking.customer.dl
                # Construct the full path to the file
                file_path = dl_file.path
                email.attach_file(file_path)
                email.send()

                messages.success(request, 'Your car has been booked successfully!')
                return redirect(profile)  # Return JSON response indicating success
            else:
                booking.delete()
                messages.error(request, 'Payment signature verification failed.')
                return redirect(profile)  # Return JSON response indicating failure
            
        except Booking.DoesNotExist:
            booking.car.booked=False
            booking.car.save()
            booking.delete()
            messages.error(request, 'Booking not found for the provided order ID.')
            return redirect(profile)  # Return JSON response indicating failure
        except Exception as e:
            booking.car.booked=False
            booking.car.save()
            booking.delete()
            messages.error(request, f'Your payment failed: {str(e)}')
            return redirect(profile)  
    return render(request, 'payment.html')  




def cancel_booking(request, booking_id):
    # Retrieve booking object
    booking = Booking.objects.get(pk=booking_id)

    # Update booking status
    amount = int(booking.amount)*100

    # Cancel payment and issue refund (if applicable)
    # if booking.payment_status == Booking.PAID:
    client = razorpay.Client(auth=("rzp_test_xJQ8e3ZkXc1mCY", "XOBYZLb5dTWcLjd4UcqEmNTw"))
    try:
            # Initiate refund request
        refund = client.payment.refund(booking.razorpay_payment_id,{
                "amount": amount,  # Amount in paisa (multiply by 100)
                "speed": "optimum"})
        print(refund)
        id=refund.get('id')
            # Check refund status
        # time.sleep(60)
        if refund.get('status') == 'processed':
                # Refund successful
            # booking.refund_status = Booking.REFUNDED
            # booking.save()

            # Sending email notification
            subject = f'Booked car cancelled'
            message = f"Dear {booking.dealer.fname} {booking.dealer.lname}, your car ({booking.car.regno} {booking.car.make} {booking.car.model}) which was booked by {booking.customer.fname} {booking.customer.lname} was cancelled."
            recipient_email = booking.dealer.email  # Assuming Car model has owner field with email
            sender_email = settings.EMAIL_HOST_USER  # Sender's email from settings
            send_mail(subject, message, sender_email, [recipient_email])

            booking.car.booked = False
            booking.car.save()
            booking.delete()
            messages.success(request, f"The booking was canceled and a refund was successfully processed. Use this id: {id} to verify your refund.")
        elif refund.get('status') == 'pending':
                # Refund failed or pending
            booking.car.booked = False
            booking.car.save()
            booking.delete()
            messages.success(request, f"The booking was canceled, but the refund is pending. Use this id: {id} to verify your refund.")
    except Exception as e:
            # Handle refund failure
        messages.error(request, f"Failed to process refund: {e}")

    # else:
    #     # Booking was not paid, no refund necessary
    #     messages.info(request, "The booking was canceled. No refund was processed.")

    return redirect(profile)




def toggle_availability(request):
    if request.method == 'POST':
        car_id = request.POST.get('car_id')
        try:
            car = Car.objects.get(id=car_id)
            car.availability = not car.availability
            car.save()
            messages.success(request, f"Availability for {car.make} {car.model} toggled successfully.")
        except Car.DoesNotExist:
            messages.error(request, "Car not found.")
        return redirect(profile)  # Redirect to the profile page after toggling availability
    else:
        return redirect(profile)  # Redirect to the profile page if not a POST request

 
def edit_car_field(request, car_id):
    if request.method == 'POST':
        price = request.POST.get('price')
        location = request.POST.get('location')

        try:
            car = Car.objects.get(id=car_id)
            if price:
                car.price = price
            if location:
                car.location = location
            car.save()
            messages.success(request, f"Changes for {car.make} {car.model} updated successfully.")
        except Car.DoesNotExist:
            messages.error(request, "Car not found.")

    return redirect(profile)



def change_booking_status(request, booking_id):
    if request.method == 'POST':
        booking = Booking.objects.get(pk=booking_id)
        if booking.car.booked:
            booking.car.booked = False
            booking.car.save()
            messages.success(request, "The booking status was successfully changed.")
        else:
            messages.error(request, "Failed to change booking status.")
            # You might want to add a failure message here
    return redirect(profile)  # Redirect to wherever you want after changing status


def deactivate_dealer(request, dealer_id):
    if request.method == 'POST':
        deal = dealer.objects.get(id=dealer_id)
        u = user.objects.get(username=deal.username)
        car = Car.objects.filter(username=deal.username)

        subject = f'Account Deactivation'
        message = f"Dear {deal.fname} {deal.lname}, your account {deal.username} is deactivated permenantly because it had violated our policy."
        recipient_email = deal.email  
        sender_email = settings.EMAIL_HOST_USER  
        send_mail(subject, message, sender_email, [recipient_email])

        car.delete()
        u.delete()
        deal.delete()
        messages.success(request, f'Dealer account ({deal.username}) deactivated successfully.')
    return redirect(profile)

def deactivate_customer(request, customer_id):
    if request.method == 'POST':
        cus = customer.objects.get(id=customer_id)
        u = user.objects.get(username=cus.username)

        subject = f'Account Deactivation'
        message = f"Dear {cus.fname} {cus.lname}, your account {cus.username} is deactivated permenantly because it had violated our policy."
        recipient_email = cus.email  
        sender_email = settings.EMAIL_HOST_USER  
        send_mail(subject, message, sender_email, [recipient_email])

        u.delete()
        cus.delete()
        messages.success(request, f'Customer account ({cus.username}) deactivated successfully.')
    return redirect(profile)


def suspend_car(request, car_id):
    # Retrieve the car object
    car = Car.objects.get(id=car_id)
    deal = dealer.objects.get(username=car.username)
    subject = f'Car Dismissal'
    message = f"Dear {deal.fname} {deal.lname}, your car ({car.regno} {car.make} {car.model}) is suspended permenantly because it had violated our policy."
    recipient_email = deal.email  
    sender_email = settings.EMAIL_HOST_USER  
    send_mail(subject, message, sender_email, [recipient_email])
    car.delete()
    return redirect(profile)