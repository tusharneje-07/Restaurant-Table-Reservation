from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from datetime import datetime
from .models import Table, Reservation, Payment, AllTransactions
from .serializers import UserSerializer, TableSerializer, ReservationSerializer, PaymentSerializer
from django.contrib.auth.models import User
from django.db.models import Count, Sum

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
    username = request.COOKIES.get('username')
    tables = Table.objects.all()
    reservations = Reservation.objects.filter(customer_username=username).order_by('-date')
    return render(request, 'yummy_main.html', {'tables': tables, 'username': username, 'reservations': reservations})

def login(request):
    return render(request, 'login.html')

def logout(request):
    response = redirect('login')
    response.delete_cookie('user')
    response.delete_cookie('username')
    response.delete_cookie('authenticated')
    return response

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
    selected_date=request.GET.get('date')
    if selected_date:
        reservations=Reservation.objects.filter(date=selected_date)
    else:
        reservations=Reservation.objects.all()

        
    return render(request, 'reservations.html', {'reservations': reservations})

# Make Reservation

def make_reservation(request):
    if request.method == 'POST':
        username = request.COOKIES.get('username')
        customer_name = request.POST['customer_name']
        contact_number=request.POST['contact_number']
        table_id = request.POST['table']
        date = request.POST['date']
        arrival_time = request.POST['arrival_time']
        departure_time = request.POST['departure_time']



        if request.POST['table']=='custom' :
            custom_seats=int(request.POST['custom_seats'])
            table=Table.objects.create(seats=custom_seats)
        else:
            table = Table.objects.get(id=table_id)

        new_reservation = Reservation(
            customer_username=username,
            customer_name=customer_name,
            contact_number=contact_number,
            table=table,
            date=date,
            arrival_time=arrival_time,
            departure_time=departure_time,
            booking_status='booked'
        )

        

        if new_reservation.is_table_available():   
            return redirect('payment_page', customer_name=customer_name, contact_number=contact_number, table_id=table.id, date=date,
                arrival_time=arrival_time, departure_time=departure_time, username=username)

        else:
            print("Table is already reserved for this time..........................................")
            return render(request, 'yummy_main.html', {'tables': Table.objects.all(), 'error': 'Table is already reserved for this time.','form_submited':True})

    return render(request, 'yummy_main.html', {'tables': Table.objects.all()})

# Payment Page

def payment_page(request, customer_name, contact_number, table_id, date, arrival_time, departure_time, username):
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
        customer_username=username,
        customer_name=customer_name,
        contact_number=contact_number,
        table=table,
        date=date,
        arrival_time=arrival_time,
        departure_time=departure_time
    )
    price = reservation.calculate_price()

    if request.method == "POST":
        username = request.COOKIES.get('username')
        payment_status = request.POST.get("payment_status")
        if payment_status == "success":
            reservation.status = "confirmed"
            reservation.save()
            new_transaction = AllTransactions.objects.create(
            customer_username=username,
            booking_id=reservation.id,
            customer_name=customer_name,
            contact_number=contact_number,
            table=table,    
            date=date,
            arrival_time=arrival_time,
            departure_time=departure_time,
            booking_status='booked',
            total_price=price
        )
            return redirect("reservation_success", status="success")
        else:
            return redirect("reservation_success", status="failed")

    return render(request, "payment.html", {
        "customer_name": customer_name,
        "contact_number": contact_number,
        "table": table,
        "date": date,
        "arrival_time": arrival_time,
        "departure_time": departure_time,
        "price": price,
        "username": username
    })

# Reservation Success Page
def reservation_success(request, status):
    return render(request, 'reservation_success.html', {'status': status})


def reservation_delete(request, reservation_id):
    try:
        reservation = get_object_or_404(AllTransactions, id=reservation_id)
        reservation.booking_status = 'cancelled'
        reservation.save()
        
        return JsonResponse({'message': 'Reservation deleted successfully', 'status': True})
    except Exception as e:
        return JsonResponse({'message': 'Reservation not found', 'status': False})


def get_analytics(request):
    
    total_bookings = Reservation.objects.count()
    table_vise_bookings = list(AllTransactions.objects.values('table').annotate(total_bookings=Count('table'),total_revenue=Sum('total_price')))
    data = {
        'total_bookings': total_bookings,
        'table_vise_bookings': table_vise_bookings,
    }
    return JsonResponse({'message': 'Analytics fetched successfully', 'status': True, 'data': data})


def hotel_login(request):
    return render(request, 'hotel_login.html')

def authenticate(request):
    username = request.POST['username']
    password = request.POST['password']
    user = User.objects.get(username=username)
    if user is not None:
        if user.check_password(password):
            response = redirect('home')
            response.set_cookie('user', user.id)
            response.set_cookie('username', user.username)
            response.set_cookie('authenticated', True)
            return response
        else:
            return render(request, 'login.html', {'error': 'Invalid password'})
    else:
        return render(request, 'login.html', {'error': 'Invalid username or password'})   

def vendor_login(request):
    return render(request, 'vendor_login.html')

def authenticate_vendor(request):
    username = request.POST['username']
    password = request.POST['password']
    if username == 'admin' and password == '123':
        response = redirect('vendor_dashboard')
        response.set_cookie('vendor', True)
        response.set_cookie('vendor_username', username)
        return response
    else:
        return render(request, 'vendor_login.html', {'error': 'Invalid username or password'})

def vendor_dashboard(request):
    if request.COOKIES.get('vendor') is None:
        return redirect('vendor_login')
    else:
        total_bookings = Reservation.objects.count()
        table_vise_bookings = list(AllTransactions.objects.values('table').annotate(total_bookings=Count('table'),total_revenue=Sum('total_price')))
        total_revenue = AllTransactions.objects.aggregate(total_revenue=Sum('total_price'))['total_revenue']
        total_table_options = Table.objects.count()
        reservations = AllTransactions.objects.all()
        return render(request, 'vendor_dashboard.html', {'total_bookings': total_bookings, 'table_vise_bookings': table_vise_bookings, 'total_revenue': total_revenue, 'total_table_options': total_table_options, 'reservations': reservations})


def vendor_logout(request):
    response = redirect('vendor_login')
    response.delete_cookie('vendor')
    response.delete_cookie('vendor_username')
    return response

