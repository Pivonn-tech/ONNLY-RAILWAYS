# ONNLY-RAILWAYS 

A premium, full-stack railway booking system designed for the Kenyan SGR network.
Built to replace legacy "list-based" booking systems with a modern, visual experience.

> **Note:** This entire project was architected and deployed using **Termux on Android**.

---

## Key Features

### 1. Visual Seat Selection
Gone are the days of random seat assignments.
- **Interactive Grid:** Visual representation of the train carriage.
- **Real-Time Availability:** Booked seats turn gray instantly.
- **Smart Validation:** Prevents double-booking and enforces max 5 seats per user.

### 2. Dynamic Pricing Engine
- **Class Logic:** Automatically detects if you select a First Class seat (Coach E) or Economy.
- **Route Math:** Calculates fares based on distance (e.g., Nairobi → Voi is cheaper than Nairobi → Mombasa).
- **Family Booking:** Handles multiple passengers in a single transaction.

### 3. Airline-Grade UI
- **Glassmorphism Design:** Modern, translucent search bars and cards.
- **QR Code Boarding Passes:** Generates a scannable QR ticket with PNR and seat details.
- **Responsive:** Works perfectly on mobile and desktop.

### 4. Admin Automation
- **Auto-Capacity:** The system automatically calculates total seats based on the number of coaches (e.g., 8 coaches × 80 seats).
- **Smart Dashboard:** Admins can manage schedules, track revenue, and view passenger manifests.

---

## Tech Stack

- **Backend:** Django 5 (Python 3.12)
- **Frontend:** HTML5, CSS3 (Custom Glassmorphism), JavaScript (DOM Manipulation)
- **Database:** SQLite3 (Dev)
- **Development Environment:** Termux (Android)

---

## How to Run

1. **Clone the repo**
   ```
   git clone [https://github.com/Pivonn-tech/ONNLY-RAILWAYS.git](https://github.com/Pivonn-tech/ONNLY-RAILWAYS.git)
   cd ONNLY-RAILWAYS
2. Install dependencies
   ```
   pip install -r requirements.txt
  
  
3. Migrate Database
   ```
   python manage.py migrate

4. Run Server
   ```
   python manage.py runserver

## Preview
   **(Screenshots coming soon)**

## ________________________________________
## Author: Pivonn-Tech | Python Enthusiast
## ________________________________________
