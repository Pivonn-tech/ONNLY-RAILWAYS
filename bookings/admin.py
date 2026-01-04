from django.contrib import admin
from .models import Train, Passenger, Station, TrainStop

# 1. INLINE: This lets you add Stops inside the Train page
class TrainStopInline(admin.TabularInline):
    model = TrainStop
    extra = 1
    ordering = ('stop_number',)

# 2. TRAIN ADMIN (The Main Train Manager)
class TrainAdmin(admin.ModelAdmin):
    list_display = ('train_name', 'train_number', 'coaches_count', 'total_seats', 'available_seats')
    
    # These fields are calculated automatically, so we make them read-only
    readonly_fields = ('total_seats', 'available_seats')
    
    # Hide the old legacy fields to avoid confusion
    exclude = ('source', 'destination', 'fare_per_seat')
    
    # Add the inline editor so you can see stops inside the Train page
    inlines = [TrainStopInline]

# 3. TRAIN STOP ADMIN (The List of all stops)
class TrainStopAdmin(admin.ModelAdmin):
    list_display = ('train', 'station', 'stop_number', 'arrival_time', 'price_from_source')
    list_filter = ('train', 'station')
    search_fields = ('train__train_name', 'station__name')
    ordering = ('train', 'stop_number')

# 4. REGISTER EVERYTHING
admin.site.register(Train, TrainAdmin)  
admin.site.register(TrainStop, TrainStopAdmin)
admin.site.register(Station)
admin.site.register(Passenger)