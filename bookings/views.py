import json
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.db.models import Sum, Count, Q
from django.contrib.admin.views.decorators import staff_member_required

from .models import Train, Passenger, Station, TrainStop
from .forms import BookingForm


# --- 1. SEARCH ---
def home(request):
    trains = None
    cities = Station.objects.values_list("name", flat=True)

    if request.method == "POST":
        src_name = request.POST.get("source")
        dest_name = request.POST.get("destination")

        if src_name and dest_name:
            possible_trains = (
                Train.objects.filter(stops__station__name=src_name)
                .filter(stops__station__name=dest_name)
                .distinct()
            )
            valid_trains = []
            for train in possible_trains:
                try:
                    src_stop = train.stops.get(station__name=src_name)
                    dest_stop = train.stops.get(station__name=dest_name)
                    if src_stop.stop_number < dest_stop.stop_number:
                        train.display_price = (
                            dest_stop.price_from_source - src_stop.price_from_source
                        )
                        train.dept_time = src_stop.departure_time
                        train.arr_time = dest_stop.arrival_time
                        valid_trains.append(train)
                except:
                    continue
            trains = valid_trains

    return render(request, "home.html", {"trains": trains, "cities": cities})


# --- 2. SEAT SELECTION ---
def select_seats(request, train_id):
    train = Train.objects.get(id=train_id)
    src_name = request.GET.get("src")
    dest_name = request.GET.get("dest")
    journey_date = request.GET.get("date")

    # Pricing
    economy_price = 0
    first_price = 0
    if src_name and dest_name:
        try:
            src_stop = train.stops.get(station__name=src_name)
            dest_stop = train.stops.get(station__name=dest_name)
            economy_price = dest_stop.price_from_source - src_stop.price_from_source
            first_price = dest_stop.first_class_price - src_stop.first_class_price
            if first_price <= 0:
                first_price = float(economy_price) * 1.5
        except:
            pass

    # Taken Seats
    taken_seats = []
    if journey_date:
        bookings = Passenger.objects.filter(train=train, date_of_journey=journey_date)
        taken_seats = list(bookings.values_list("seat_number", flat=True))

    rows_to_show = int(train.seats_per_coach / 4)

    return render(
        request,
        "select_seats.html",
        {
            "train": train,
            "src": src_name,
            "dest": dest_name,
            "date": journey_date,
            "economy_price": economy_price,
            "first_price": first_price,
            "taken_seats_json": json.dumps(taken_seats),
            "total_rows": rows_to_show,
        },
    )


# --- 3. BOOKING ---
@login_required
def book_ticket(request, train_id):
    train = Train.objects.get(id=train_id)

    # 1. Grab Data from URL
    src = request.GET.get("src")
    dest = request.GET.get("dest")
    selected_seats_str = request.GET.get("selected_seats", "") 
    
    # CLEAN THE DATA: Split by comma AND strip spaces
    # Example: "E-1A, E-1B" -> ['E-1A', 'E-1B']
    seat_list = [s.strip() for s in selected_seats_str.split(',') if s.strip()]
    seat_count = len(seat_list) if seat_list else 1

    # Debugging: Print to your terminal to see what's happening
    print(f"DEBUG: Seats received: {seat_list}")

    # 2. Calculate Price Per Person
    price_per_seat = train.fare_per_seat 
    
    try:
        # Use filter().first() to avoid crashes
        src_stop = train.stops.filter(station__name=src).first()
        dest_stop = train.stops.filter(station__name=dest).first()

        if src_stop and dest_stop:
            # Base Economy Price
            base_price = dest_stop.price_from_source - src_stop.price_from_source
            
            # --- THE FIX: ROBUST FIRST CLASS CHECK ---
            is_first_class = False
            
            # Check the first seat. If it starts with 'E' or 'E-', it's First Class.
            if seat_list:
                first_seat = str(seat_list[0]).upper() # Force uppercase
                if first_seat.startswith('E'):         # 'E-1A' or 'E1A'
                    is_first_class = True
            
            if is_first_class:
                 print("DEBUG: Detected First Class!")
                 diff = dest_stop.first_class_price - src_stop.first_class_price
                 # Use difference if set, otherwise 1.5x economy
                 price_per_seat = diff if diff > 0 else float(base_price) * 1.5
            else:
                 print("DEBUG: Detected Economy Class")
                 price_per_seat = base_price

    except Exception as e:
        print(f"Price Calculation Error: {e}")
        pass

    total_price = float(price_per_seat) * int(seat_count)

    # 3. Handle Payment
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            saved_tickets = []
            final_seats = seat_list if seat_list else ["UNASSIGNED"]

            for seat_num in final_seats:
                ticket = form.save(commit=False)
                ticket.user = request.user
                ticket.train = train
                ticket.source = src
                ticket.destination = dest
                ticket.paid_amount = price_per_seat
                ticket.seat_number = str(seat_num)
                ticket.save()
                saved_tickets.append(ticket)

            # Update availability
            if train.available_seats and train.available_seats >= len(final_seats):
                train.available_seats -= len(final_seats)
                train.save()

            if len(saved_tickets) > 1:
                return redirect('dashboard')
            else:
                return render(request, "ticket.html", {"passenger": saved_tickets[0]})

    else:
        initial = {
            "train": train, 
            "source": src, 
            "destination": dest,
            "name": request.user.username, 
            "date_of_journey": request.GET.get("date")
        }
        form = BookingForm(initial=initial)

    return render(request, "book.html", {
        "form": form, 
        "train": train, 
        "price": total_price, 
        "src": src, 
        "dest": dest, 
        "seat_count": seat_count, 
        "seats": selected_seats_str
    })

# --- 4. EXTRAS ---
@login_required
def dashboard(request):
    my_tickets = Passenger.objects.filter(user=request.user).order_by(
        "-date_of_journey"
    )
    return render(request, "dashboard.html", {"tickets": my_tickets})


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "signup.html", {"form": form})


def custom_logout(request):
    logout(request)
    return redirect("home")


@login_required
def cancel_ticket(request, ticket_id):
    try:
        t = Passenger.objects.get(id=ticket_id)
        if t.user == request.user:
            t.train.available_seats += 1
            t.train.save()
            t.delete()
    except:
        pass
    return redirect("dashboard")


@staff_member_required
def admin_dashboard(request):
    # Analytics logic here...
    return render(request, "analytics.html", {})
