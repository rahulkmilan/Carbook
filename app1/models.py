from django.db import models

# Create your models here.
class customer(models.Model):
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    email = models.EmailField()
    pno = models.CharField(max_length=10)
    dl = models.ImageField(upload_to='media/')
    username = models.CharField(max_length=50)
    def __str__(self):
        return self.username

class dealer(models.Model):
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    email = models.EmailField()
    pno = models.CharField(max_length=10)
    ad = models.ImageField(upload_to='media/')
    username = models.CharField(max_length=50)
    def __str__(self):
        return self.username
    

class user(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    status = models.IntegerField()
    def __str__(self):
        return self.username


class Car(models.Model):
    username = models.CharField(max_length=50)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    regno = models.CharField(max_length=20, unique=True)
    price = models.IntegerField()
    location = models.CharField(max_length=100)
    rc = models.ImageField(upload_to='rc_books/')
    photos = models.ImageField(upload_to='car_photos/')
    status = models.CharField(max_length=12)
    availability = models.BooleanField(default=True)
    rejection_reason = models.TextField(blank=True)
    booked = models.BooleanField(default=False)
    
    def __str__(self):
        return self.regno+ " - "+self.make+" "+self.model+" "+self.username


class Booking(models.Model):
    username = models.CharField(max_length=50)
    regno = models.CharField(max_length=20)
    dropoff_location = models.CharField(max_length=100)
    dropoff_date = models.DateField()
    dropoff_time = models.TimeField()
    nod = models.IntegerField()
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    customer = models.ForeignKey(customer, on_delete=models.CASCADE)
    dealer = models.ForeignKey(dealer, on_delete=models.CASCADE)
    amount = models.CharField(max_length=100)
    order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    paid = models.BooleanField(default=False)
    
    def __str__(self):
        return self.regno
