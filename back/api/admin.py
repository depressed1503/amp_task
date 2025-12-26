from django.contrib import admin
from .models import Event, Booking


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "total_seats")
    search_fields = ("name",)
    ordering = ("id",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "user", "created_at")
    list_select_related = ("event", "user")
    list_filter = ("event", "created_at")
    search_fields = ("event__name", "user__username", "user__email")
    ordering = ("-created_at",)
