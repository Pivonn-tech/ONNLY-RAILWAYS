from django.contrib import admin
from django.urls import path, include  # Add 'include'
from bookings import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("book/<int:train_id>/", views.book_ticket, name="book_ticket"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("cancel/<int:ticket_id>/", views.cancel_ticket, name="cancel_ticket"),
    path('manager/analytics/', views.admin_dashboard, name='analytics'),
    path('select-seats/<int:train_id>/', views.select_seats, name='select_seats'),

    # User Auth URLs
    path("signup/", views.signup, name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
]
