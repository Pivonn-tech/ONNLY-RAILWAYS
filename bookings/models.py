from django.db import models
from django.contrib.auth.models import User

class Train(models.Model):
    train_number = models.CharField(max_length=10, unique=True)
    train_name = models.CharField(max_length=100)
    
    # Configuration
    coaches_count = models.IntegerField(default=8, help_text="Standard is 8 cars")
    seats_per_coach = models.IntegerField(default=80, help_text="Standard is 80 for Economy")
    
    # Automated fields
    total_seats = models.IntegerField(null=True, blank=True)
    available_seats = models.IntegerField(null=True, blank=True)

    # Legacy fields (kept for safety)
    source = models.CharField(max_length=100, blank=True, null=True)
    destination = models.CharField(max_length=100, blank=True, null=True)
    fare_per_seat = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True)

    def save(self, *args, **kwargs):
        # 1. Auto-Calculate Total Seats
        self.total_seats = self.coaches_count * self.seats_per_coach
        # 2. Initialize Available Seats if new
        if self.available_seats is None:
            self.available_seats = self.total_seats
        super().save(*args, **kwargs)

    @property
    def get_real_source(self):
        first = self.stops.first()
        return first.station.name if first else "No Schedule"

    @property
    def get_real_destination(self):
        last = self.stops.last()
        return last.station.name if last else "No Schedule"

    def __str__(self):
        return f"{self.train_name} ({self.train_number})"


class Passenger(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    date_of_journey = models.DateField()
    
    # CHANGED: CharField to allow "E-1A"
    seat_number = models.CharField(max_length=10, null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.seat_number}"


class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class TrainStop(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="stops")
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    stop_number = models.IntegerField()
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    
    # Prices
    price_from_source = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    first_class_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ["stop_number"]

    def __str__(self):
        return f"{self.train.train_name} - {self.station.name}"