from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
import datetime


# Create your models here.

class Location(models.Model):
    city = models.CharField(max_length= 30)

class Plane(models.Model):
    noOfEconomy = models.IntegerField(default = 0, validators=[MinValueValidator(0)])
    noOfBusiness = models.IntegerField(default = 0, validators=[MinValueValidator(0)])
    noOfFirstClass = models.IntegerField(default = 0, validators=[MinValueValidator(0)])

class Price(models.Model):
    # flightID = models.ForeignKey(Flight, on_delete=models.CASCADE)
    priceOfEconomy = models.DecimalField(max_digits= 7, decimal_places=2)
    priceOfBusiness = models.DecimalField(max_digits= 7, decimal_places=2)
    priceOfFirstClass = models.DecimalField(max_digits= 7, decimal_places=2)
    currency = models.CharField(max_length= 3)
    
class Flight(models.Model):
    planeID = models.ForeignKey(Plane, on_delete=models.CASCADE)
    priceID = models.ForeignKey(Price, on_delete=models.CASCADE, null = True)
    startLocation = models.ForeignKey(Location, on_delete=models.CASCADE, related_name = "start_location")
    destination = models.ForeignKey(Location, on_delete=models.CASCADE, related_name = "destination_location")
    airline = models.CharField(max_length= 30)
    noOfPassengers = models.IntegerField(default = 0, validators=[MinValueValidator(0)])
    totalAvailableSeats = models.IntegerField(default = 0, validators=[MinValueValidator(0)])
    availableSeatsEconomy = models.IntegerField(default = 0, validators=[MinValueValidator(0)])
    availableSeatsBusiness = models.IntegerField(default = 0, validators=[MinValueValidator(0)])
    availableSeatsFirstClass = models.IntegerField(default = 0, validators=[MinValueValidator(0)])
    departureDate = models.DateField(default=timezone.now().date())
    departureTime = models.TimeField(default=timezone.now().time())
    arrivalDate = models.DateField(default=timezone.now().date())
    arrivalTime = models.TimeField(default=timezone.now().time())
    flightDuration = models.TimeField(default=datetime.time(hour=0, minute=0))

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         # Set default values for available seats based on the associated Plane object
    #         self.availableSeatsEconomy = self.planeID.noOfEconomy
    #         self.availableSeatsBusiness = self.planeID.noOfBusiness
    #         self.availableSeatsFirstClass = self.planeID.noOfFirstClass
    #     super().save(*args, **kwargs)


class Passenger(models.Model):
    email = models.CharField(max_length= 120)

class Reservation(models.Model):
    passengerID = models.ForeignKey(Passenger, on_delete=models.CASCADE, null = True)
    flightID = models.ForeignKey(Flight, on_delete=models.CASCADE)
    noOfEconomy = models.IntegerField(default = 0, validators=[MinValueValidator(0)])
    noOfBusiness = models.IntegerField(default = 0,validators=[MinValueValidator(0)])
    noOfFirstClass = models.IntegerField(default = 0, validators=[MinValueValidator(0)])
    confirmedStatus = models.BooleanField(default=False)
    timeStarted = models.DateTimeField()




    

