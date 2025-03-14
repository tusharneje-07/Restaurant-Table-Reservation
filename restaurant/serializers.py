from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Table, Reservation, Payment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','email']


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'

    def validate(self, data):
        """Ensure no overlapping reservations exist."""
        table = data['table']
        date = data['date']
        arrival_time = data['arrival_time']
        departure_time = data['departure_time']

        overlapping_reservations = Reservation.objects.filter(
            table=table,
            date=date
        ).filter(
            arrival_time__lt=departure_time,
            departure_time__gt=arrival_time
        )

        if overlapping_reservations.exists():
            raise serializers.ValidationError("This table is already reserved during this time.")

        return data

