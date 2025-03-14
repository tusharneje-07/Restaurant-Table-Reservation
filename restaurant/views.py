from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from datetime import datetime
from .models import Table, Reservation, Payment
from .serializers import UserSerializer, TableSerializer, ReservationSerializer, PaymentSerializer
from django.contrib.auth.models import User

# User API
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Table API
class TableListCreateView(generics.ListCreateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

# Reservation API
class ReservationListCreateView(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

# Payment API
class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

# Home Page
def home(request):
    return render(request, 'home.html')

# Create Reservation
class ReservationCreateView(generics.CreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Table reserved successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# List Reservations
def reservation_list(request):
    reservations = Reservation.objects.all()
    return render(request, 'reservations.html', {'reservations': reservations})

# Make Reservation

def make_reservation(request):
    if request.method == 'POST':
        customer_name = request.POST['customer_name']
        table_id = request.POST['table']
        date = request.POST['date']
        arrival_time = request.POST['arrival_time']
        departure_time = request.POST['departure_time']

        table = Table.objects.get(id=table_id)
        new_reservation = Reservation(
            customer_name=customer_name,
            table=table,
            date=date,
            arrival_time=arrival_time,
            departure_time=departure_time
        )

        if new_reservation.is_table_available():
            return redirect('payment_page', customer_name=customer_name, table_id=table.id, date=date,
                            arrival_time=arrival_time, departure_time=departure_time)
        else:
            return render(request, 'make_reservation.html', {'tables': Table.objects.all(), 'error': 'Table is already reserved for this time.'})

    return render(request, 'make_reservation.html', {'tables': Table.objects.all()})

# Payment Page

def payment_page(request, customer_name, table_id, date, arrival_time, departure_time):
    table = get_object_or_404(Table, id=table_id)
    try:
        arrival_time = datetime.strptime(arrival_time, "%H:%M:%S").time()
    except ValueError:
        arrival_time = datetime.strptime(arrival_time, "%H:%M").time()

    try:
        departure_time = datetime.strptime(departure_time, "%H:%M:%S").time()
    except ValueError:
        departure_time = datetime.strptime(departure_time, "%H:%M").time()

    reservation = Reservation(
        customer_name=customer_name,
        table=table,
        date=date,
        arrival_time=arrival_time,
        departure_time=departure_time
    )
    price = reservation.calculate_price()

    if request.method == "POST":
        payment_status = request.POST.get("payment_status")
        if payment_status == "success":
            reservation.status = "confirmed"
            reservation.save()
            return redirect("reservation_success", status="success")
        else:
            return redirect("reservation_success", status="failed")

    return render(request, "payment.html", {
        "customer_name": customer_name,
        "table": table,
        "date": date,
        "arrival_time": arrival_time,
        "departure_time": departure_time,
        "price": price
    })

# Reservation Success Page
def reservation_success(request, status):
    return render(request, 'reservation_success.html', {'status': status})
