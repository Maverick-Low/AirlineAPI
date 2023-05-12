from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from .models import Flight, Reservation, Location, Passenger
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
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

@require_GET
def list_flights(request):
    
    try: 
        cancel_old_reservations()
        data = json.loads(request.body) # {dateOfDeparture, "cityOfDeparture", cityOfArrival, ‘tickets" }
        departureDateString = data.get('dateOfDeparture') # String
        departureCity = data.get('cityOfDeparture')  # String
        arrivalCity = data.get('cityOfArrival') # String
        totalTickets = data.get('‘tickets')# Int

        departureDate = datetime.strptime(departureDateString, "%Y-%m-%d") if departureDateString else None
        departureCityID = Location.objects.get(city__iexact = departureCity) if departureCity else None
        arrivalCityID = Location.objects.get(city__iexact = arrivalCity) if arrivalCity else None

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
                            "dateOfDeparture" : flight.departureDate,
                            "timeOfDeparture" : flight.departureTime,
                            "timeOfArrival" : flight.arrivalTime,
                            "seats": {
                                "noOfEconomy": flight.planeID.noOfEconomy,
                                "noOfBusiness": flight.planeID.noOfBusiness,
                                "noOfFirstClass": flight.planeID.noOfFirstClass,
                            },
                                "price" : {
                                    "priceOfEconomy": flight.priceID.priceOfEconomy,
                                    "priceOfBusiness": flight.priceID.priceOfBusiness,
                                    "priceOfFirstClass": flight.priceID.priceOfFirstClass
                            }
                        }
            
            flightID = "01" + str(flight.pk)
            listOfFlights[flightID] = flightDict

        return JsonResponse(listOfFlights)
    
    except ObjectDoesNotExist:
        return JsonResponse({"status" : "failed"})

# {
#     "flightID": "011",
#     "seats": {
#         "noOfEconomy": 3,
#         "noOfBusiness": 2,
#         "noOfFirstClass": 1
#     },
#     "email" : "maverick@gmail.com"
# }

@csrf_exempt
def start_reservation_process(request):

    try:
        cancel_old_reservations()
        data = json.loads(request.body) #  {flightID’, "seats : {noOfEconomy, noOfBusiness, noOfFirstClass}, "email"}
        flightID = data.get('flightID') # Int
        noOfSeats = data.get('seats', 0)# Int
        email = data.get('email') # String

        parsedFlightID = int(flightID[2:])
        economySeats = noOfSeats.get('noOfEconomy', 0) # Int
        businessSeats = noOfSeats.get('noOfBusiness', 0) # Int
        firstClassSeats = noOfSeats.get('noOfFirstClass', 0) # Int

        flight = Flight.objects.get(pk = parsedFlightID)

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

        bookingID = "01" + str(reservation.pk)
        return JsonResponse({"bookingID": bookingID})
    
    except ObjectDoesNotExist:
        return JsonResponse({"status": "failed"})

# {"bookingID" : "0115"}

@csrf_exempt
def cancel_reservation(request): 
    
    try:
        cancel_old_reservations()
        data = json.loads(request.body)  #  {"bookingID"}
        reservationID = data.get('bookingID') # String
        bookingID = reservationID[2:]
        reservation = Reservation.objects.get(pk = bookingID)

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
        return JsonResponse({"status": "success"})

    except ObjectDoesNotExist:
        return JsonResponse({"status": "failed"})

@csrf_exempt
def confirm_booking(request):
    try:
        cancel_old_reservations()
        data = json.loads(request.body)  #  {"bookingID", "amount"}
        reservationID = data.get('bookingID') # String
        bookingID = reservationID[2:]
        amount = data.get('amount') # amount

        reservation = Reservation.objects.get(pk = bookingID)
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
            return JsonResponse({"status": "success"})
        
        else:
            return JsonResponse({"status": "failed"})
    
    except ObjectDoesNotExist:
        return JsonResponse({"status": "failed"})
    
@csrf_exempt    
def cancel_booking(request):
    try:
        cancel_old_reservations()
        data = json.loads(request.body)  #  {"bookingID"}
        reservationID = data.get('bookingID') # Int
        bookingID = reservationID[2:]
        reservation = Reservation.objects.get(pk = bookingID)

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
        return JsonResponse({"status": "success"})

    except ObjectDoesNotExist:
        return JsonResponse({"status": "failed"})

def cancel_old_reservations():
    currentTime = timezone.now()
    fifteenMinsAgo = currentTime - timedelta(minutes=15)
    oldReservations = Reservation.objects.filter(timeStarted__lte = fifteenMinsAgo, confirmedStatus = 0)
    for reservation in oldReservations:
        # Add number of seats back to flight
        flight = reservation.flightID
        totalSeats = reservation.noOfEconomy + reservation.noOfBusiness + reservation.noOfFirstClass
        flight.totalAvailableSeats += totalSeats
        flight.availableSeatsEconomy += reservation.noOfEconomy
        flight.availableSeatsBusiness += reservation.noOfBusiness
        flight.availableSeatsFirstClass += reservation.noOfFirstClass
        flight.save()
        reservation.delete()