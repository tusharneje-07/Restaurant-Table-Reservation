from django.urls import path
from . import views
from .views import UserCreateView, TableListCreateView, ReservationListCreateView, PaymentListCreateView,home,reservation_list,make_reservation,payment_page

urlpatterns = [
    path('user_login/',views.login,name='login'),
    path('',home,name='home'),
    path('hotel-login/',views.hotel_login,name='hotel_login'),
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('tables/', TableListCreateView.as_view(), name='table-list-create'),
    path('reservations/', views.reservation_list,name='reservation_list'),
    path('reservation-delete/<int:reservation_id>/', views.reservation_delete, name='reservation_delete'),
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('make-reservation/', views.make_reservation, name='make_reservation'),
    path('payment/<str:customer_name>/<str:contact_number>/<int:table_id>/<str:date>/<str:arrival_time>/<str:departure_time>/<str:username>/', views.payment_page, name='payment_page'),
    path('reservation-success/<str:status>/', views.reservation_success, name='reservation_success'),
    
    path('get-analytics/', views.get_analytics, name='get_analytics'),
    
    
    # Authentication Endpoints
    path('authenticate/',views.authenticate,name='authenticate'),
    path('logout/', views.logout, name='logout'),
    
    
    # Vendor Endpoints
    path('authenticate_vendor/',views.authenticate_vendor,name='authenticate_vendor'),
    path('vendor-login/',views.vendor_login,name='vendor_login'),
    path('vendor-dashboard/',views.vendor_dashboard,name='vendor_dashboard'),
    path('vendor-logout/',views.vendor_logout,name='vendor_logout'),
]


