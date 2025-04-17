from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.forms import ValidationError
from django.core.validators import RegexValidator
from django.contrib import admin

class Table(models.Model):
    id = models.AutoField(primary_key=True)
    seats = models.IntegerField()

    def __str__(self):
        return f"Table {self.id} (Seats: {self.seats})"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]
    customer_username = models.CharField(max_length=100,default='0')
    customer_name = models.CharField(max_length=100)
    contact_number=models.CharField(
        max_length=10 ,
        default='9999999999',
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Enter 10 digit contact number',
                code='invalid_contact_number'
            )
        ]
    )
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    date = models.DateField()
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    status = models.CharField(
        max_length=10, 
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('failed', 'Failed')], 
        default='pending'
    )
    booking_status = models.CharField(
        max_length=10,
        choices=[('booked', 'booked'), ('cancelled', 'cancelled')],
        default='booked'
    )
    
    def is_table_available(self):
        
        overlapping_reservations = Reservation.objects.filter(
            table=self.table,
            date=self.date,
            arrival_time__lt=self.departure_time,
            departure_time__gt=self.arrival_time,
        ).exists()
        return not overlapping_reservations  # True if available, False if not

    def __str__(self):
        return f"{self.customer_name} - Table {self.table.id} - {self.date} ({self.arrival_time} - {self.departure_time})"


    def calculate_price(self):
   
        # Convert times to timedelta for duration calculation
        arrival = timedelta(hours=self.arrival_time.hour, minutes=self.arrival_time.minute)
        departure = timedelta(hours=self.departure_time.hour, minutes=self.departure_time.minute)

        duration = (departure - arrival).total_seconds() / 3600  # Convert to hours
        price_per_seat_per_hour = 30  

       
        total_price = round(duration * price_per_seat_per_hour * self.table.seats)
        
        return total_price


    def clean(self):
        """Check for overlapping reservations."""
        overlapping_reservations = Reservation.objects.filter(
            table=self.table,
            date=self.date
        ).exclude(id=self.id).filter(
            arrival_time__lt=self.departure_time,
            departure_time__gt=self.arrival_time
        )

        if overlapping_reservations.exists():
            raise ValidationError("This table is already reserved during this time.")

    def save(self, *args, **kwargs):
        """Validate and calculate price before saving."""
        self.clean()
        self.total_price = self.calculate_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation for {self.customer_name} on {self.date} from {self.arrival_time} to {self.departure_time}"

# Payment Model
class Payment(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed')
    ], default='Pending')
    
    payment_method = models.CharField(max_length=50, default='UPI')  # Set a default payment method

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
    

class AllTransactions(models.Model):
    customer_username = models.CharField(max_length=100,default='0')
    booking_id = models.CharField(max_length=50,default='0')
    customer_name = models.CharField(max_length=100)
    contact_number=models.CharField(
        max_length=10 ,
        default='9999999999',
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Enter 10 digit contact number',
                code='invalid_contact_number'
            )
        ]
    )
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    date = models.DateField()
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    status = models.CharField(
        max_length=10, 
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('failed', 'Failed')], 
        default='pending'
    )
    booking_status = models.CharField(
        max_length=10,
        choices=[('booked', 'booked'), ('cancelled', 'cancelled')],
        default='booked'
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.TextField()
    
    def __str__(self):
        return self.name
    
    
    
admin.site.register(Table)
admin.site.register(Reservation)
admin.site.register(Payment)
admin.site.register(AllTransactions)
admin.site.register(MenuItem)







