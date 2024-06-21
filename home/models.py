
import datetime
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth.models import User
from mlxtend.frequent_patterns import fpgrowth
import pandas as pd

class Location(models.Model):
    location = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.location

class CarDealer(models.Model):
    car_dealer = models.OneToOneField(User, on_delete=models.CASCADE)
    phone =  models.CharField(validators = [MinLengthValidator(10), MaxLengthValidator(15)], max_length = 15)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    earnings = models.IntegerField(default=0)
    type = models.CharField(max_length=20, blank=True)
    easypaisa_number = models.CharField(max_length=15)

    def __str__(self):
        return str(self.car_dealer)

from django.db import models

from django.db import models
class Car(models.Model):
    CATEGORY_CHOICES = [
        ('jewelry', 'Jewelry'),
        ('books', 'Books'),
        ('furniture', 'Furniture'),
        ('electronics', 'Electronics'),
        ('dresses', 'Dresses'),
        ('house', 'House'),
        ('vehicle', 'Vehicle'),
    ]

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/')
    capacity = models.IntegerField()
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='jewelry')

    car_dealer = models.ForeignKey(CarDealer, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)  # Add this line

    def __str__(self):
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(validators=[MinLengthValidator(10), MaxLengthValidator(15)], max_length=15)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, blank=True)


    def __str__(self):
        return str(self.user)
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('done', 'Done'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car_dealer = models.ForeignKey(CarDealer, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    rent = models.CharField(max_length=10)
    days = models.CharField(max_length=3)
    is_complete = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    card = models.CharField(max_length=20)
    borrow_from = models.DateField(default=datetime.date.today)  # New field for borrowing start date
    borrow_to = models.DateField(default=datetime.date.today)  # New field for borrowing end date
    cnic_front = models.ImageField(upload_to='cnic_images/', null=True, blank=True)
    cnic_back = models.ImageField(upload_to='cnic_images/', null=True, blank=True)


class UserPayment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment_boolean = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=500)











