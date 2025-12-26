from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Event, Booking

User = get_user_model()


class EventSerializer(serializers.ModelSerializer):
    booked_count = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = ["id", "name", "total_seats", "booked_count", "available_seats"]


class BookingSerializer(serializers.ModelSerializer):
    # Чтобы удобно читать
    event_name = serializers.CharField(source="event.name", read_only=True)
    user_display = serializers.CharField(source="user.get_username", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "event", "event_name", "user", "user_display", "created_at"]
        read_only_fields = ["id", "created_at", "event_name", "user_display"]
