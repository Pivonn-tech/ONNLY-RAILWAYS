from django import forms
from .models import Train, Passenger

class BookingForm(forms.ModelForm):
    class Meta:
        model = Passenger
        # We only ask the user for these fields.
        # Seat number and Fare are calculated by the system, not typed by the user.
        fields = ['name', 'train', 'source', 'destination', 'date_of_journey']
        
        # This makes the date picker appear in the browser
        widgets = {
            'date_of_journey': forms.DateInput(attrs={'type': 'date'}),
        }
