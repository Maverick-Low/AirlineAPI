from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path ('airline/form', views.list_flights),
    path ('airline/reserve', views.start_reservation_process),
    path ('airline/cancel_reservation', views.cancel_reservation),
    path ('airline/confirm_booking', views.confirm_booking),
    path ('airline/cancel_booking', views.cancel_booking),
]