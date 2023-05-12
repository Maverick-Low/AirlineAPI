from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from .models import Flight, Reservation, Location, Passenger
import json

# Create your views here.
def index(request):
    return HttpResponse("<h1> Homepage </h1>") 

# {
#     "dateOfDeparture": "",
#     "cityOfDeparture": "",
#     "cityOfArrival": "",
#     "tickets": 51
# }

def list_flights(request):
    
    try: 
        data = json.loads(request.body) # {dateOfDeparture, 'cityOfDeparture', cityOfArrival, ‘tickets' }
        departureDateString = data[list(data.keys())[0]] # String
        departureCity = data[list(data.keys())[1]] # String
        arrivalCity = data[list(data.keys())[2]] # String
        totalTickets = data[list(data.keys())[3]] # Int

        departureDate = datetime.strptime(departureDateString, '%Y-%m-%d') if departureDateString else None
        departureCityID = Location.objects.get(city = departureCity) if departureCity else None
        arrivalCityID = Location.objects.get(city = arrivalCity) if arrivalCity else None

        flights = Flight.objects.all()
        if departureCityID:
            flights = flights.filter(startLocation=departureCityID)
        if arrivalCityID:
            flights = flights.filter(destination=arrivalCityID)
        if totalTickets:
            flights = flights.filter(totalAvailableSeats__gte=totalTickets)
        if departureDate:
            flights = flights.filter(departureDate__gte=departureDate)

        listOfFlights = {}
        for flight in flights:
            flightDict = {  
                            'dateOfDeparture' : flight.departureDate,
                            'timeOfDeparture' : flight.departureTime,
                            'timeOfArrival' : flight.arrivalTime,
                            'seats': {
                                'noOfEconomy': flight.planeID.noOfEconomy,
                                'noOfBusiness': flight.planeID.noOfBusiness,
                                'noOfFirstClass': flight.planeID.noOfFirstClass,
                            },
                                'price' : {
                                    'priceOfEconomy': flight.priceID.priceOfEconomy,
                                    'priceOfBusiness': flight.priceID.priceOfBusiness,
                                    'priceOfFirstClass': flight.priceID.priceOfFirstClass
                            }
                        }
            
            flightID = '01' + str(flight.pk)
            listOfFlights[flightID] = flightDict

        return JsonResponse(listOfFlights)
    
    except ObjectDoesNotExist:
        return JsonResponse({"message" : "error"})

# {
#     "flightID": "1",
#     "Seats": {
#         "noOfEconomy": 5,
#         "noOfBusiness": 10,
#         "noOfFirstClass": 15
#     },
#     "email" : "maverick@gmail.com"
# }
  
def start_reservation_process(request):
    data = json.loads(request.body) #  {‘Flight ID’, 'Seats : {noOfEconomy, noOfBusiness, noOfFirstClass}, 'email'}
    flightID = data[list(data.keys())[0]] # Int
    noOfSeats = data[list(data.keys())[1]] # Int
    email = data[list(data.keys())[2]] # String

    economySeats = noOfSeats[list(noOfSeats.keys())[0]] # Int
    businessSeats = noOfSeats[list(noOfSeats.keys())[1]]# Int
    firstClassSeats = noOfSeats[list(noOfSeats.keys())[2]] # Int

    flight = Flight.objects.get(pk = flightID)

    # Reduce available seats from the flight
    totalSeats = economySeats + businessSeats + firstClassSeats
    flight.totalAvailableSeats -= totalSeats
    flight.availableSeatsEconomy -= economySeats
    flight.availableSeatsBusiness -= businessSeats
    flight.availableSeatsFirstClass -= firstClassSeats
    flight.save()

    # Search for passenger in passenger table, if not present, create new passenger instance
    newPassenger, created = Passenger.objects.get_or_create(email = email)
    if not created:
        newPassenger.email = email
        newPassenger.save()

    # Add reservation to the table
    reservation = Reservation(
        passengerID = newPassenger,
        flightID= flight,
        noOfEconomy = economySeats,
        noOfBusiness = businessSeats,
        noOfFirstClass= firstClassSeats,
        confirmedStatus = False,
        timeStarted = timezone.now()
    )
    reservation.save()

    response = {'bookingID': reservation.pk}
    return JsonResponse(response)

# {"ReservationID" : 15}

def cancel_reservation(request): 

    try:
        data = json.loads(request.body)  #  {'bookingID'}
        reservationID = data[list(data.keys())[0]] # Int
        reservation = Reservation.objects.get(pk = reservationID)

        if(reservation):
            # Add number of seats back to flight
            flight = reservation.flightID
            totalSeats = reservation.noOfEconomy + reservation.noOfBusiness + reservation.noOfFirstClass
            flight.totalAvailableSeats += totalSeats
            flight.availableSeatsEconomy += reservation.noOfEconomy
            flight.availableSeatsBusiness += reservation.noOfBusiness
            flight.availableSeatsFirstClass += reservation.noOfFirstClass
            flight.save()

        # Delete reservation
        reservation.delete()
        return JsonResponse({'status': "success"})

    except ObjectDoesNotExist:
        return JsonResponse({'status': "failed"})


def confirm_booking(request):
    try:
        data = json.loads(request.body)  #  {'bookingID', 'amount'}
        reservationID = data[list(data.keys())[0]] # Int
        amount = data[list(data.keys())[1]] # amount

        reservation = Reservation.objects.get(pk = reservationID)
        flight = reservation.flightID

        economyPrice = (flight.priceID.priceOfEconomy * reservation.noOfEconomy) 
        businessPrice = (flight.priceID.priceOfBusiness * reservation.noOfEconomy)
        firstClassPrice = (flight.priceID.priceOfFirstClass * reservation.noOfFirstClass)
        totalPrice =  economyPrice + businessPrice + firstClassPrice
        
        # Make sure both are formatted 2 d.p
        totalPrice2DP = round(totalPrice, 2)

        if(amount == totalPrice2DP):
            reservation.confirmedStatus = True
            reservation.save()
            return JsonResponse({'status': "success"})
        
        else:
            return JsonResponse({'status': "failed"})
    
    except ObjectDoesNotExist:
        return JsonResponse({'status': "failed"})
    

def cancel_booking(request):
    try:
        data = json.loads(request.body)  #  {'bookingID'}
        reservationID = data[list(data.keys())[0]] # Int
        # reservation = get_object_or_404(Reservation, pk = reservationID)
        reservation = Reservation.objects.get(pk = reservationID)

        if(reservation):
            # Add number of seats back to flight
            flight = reservation.flightID
            totalSeats = reservation.noOfEconomy + reservation.noOfBusiness + reservation.noOfFirstClass
            flight.totalAvailableSeats += totalSeats
            flight.availableSeatsEconomy += reservation.noOfEconomy
            flight.availableSeatsBusiness += reservation.noOfBusiness
            flight.availableSeatsFirstClass += reservation.noOfFirstClass
            flight.save()

        # Delete reservation
        reservation.delete()
        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'failed'})

