from django.urls import path
from . import views
from .views import UserCreateView, TableListCreateView, ReservationListCreateView, PaymentListCreateView,home,reservation_list,make_reservation,payment_page

urlpatterns = [
    path('',home,name='home'),
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('tables/', TableListCreateView.as_view(), name='table-list-create'),
    path('reservations/', views.reservation_list,name='reservation_list'),
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('make-reservation/', views.make_reservation, name='make_reservation'),
    path('payment/<str:customer_name>/<int:table_id>/<str:date>/<str:arrival_time>/<str:departure_time>/', views.payment_page, name='payment_page'),
    path('reservation-success/<str:status>/', views.reservation_success, name='reservation_success'),
    
]


