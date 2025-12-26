from django.db import transaction, IntegrityError
from django.db.models import Count, F, Value, IntegerField
from django.db.models.functions import Greatest
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event, Booking
from .serializers import EventSerializer, BookingSerializer


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def get_queryset(self):
        return (
            Event.objects
            .annotate(
                booked_count=Count("bookings"),
                available_seats=Greatest(
                    Value(0),
                    F("total_seats") - Count("bookings"),
                    output_field=IntegerField()
                ),
            )
        )


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    queryset = Booking.objects.select_related("event", "user").all()

    def create(self, request, *args, **kwargs):
        """
        POST /bookings/
        { "event": 1, "user": 5 }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_id = serializer.validated_data["event"].id
        user_id = serializer.validated_data["user"].id

        try:
            with transaction.atomic():
                event = Event.objects.select_for_update().filter(id=event_id).first()
                if not event:
                    return Response({"detail": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

                booked = Booking.objects.filter(event_id=event_id).count()
                if booked >= event.total_seats:
                    return Response({"detail": "No seats available"}, status=status.HTTP_409_CONFLICT)

                booking = Booking.objects.create(event_id=event_id, user_id=user_id)

        except IntegrityError:
            return Response(
                {"detail": "User already reserved this event"},
                status=status.HTTP_409_CONFLICT,
            )

        out = self.get_serializer(booking)
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(methods=["post"], detail=False, url_path="reserve")
    def reserve(self, request):
        """
        POST /bookings/reserve/
        { "event": 1, "user": 5 }
        """
        return self.create(request)

    @action(methods=["post"], detail=False, url_path="cancel")
    def cancel(self, request):
        """
        POST /bookings/cancel/
        { "event": 1, "user": 5 }
        """
        event_id = request.data.get("event")
        user_id = request.data.get("user")
        if not event_id or not user_id:
            return Response(
                {"detail": "Fields 'event' and 'user' are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted, _ = Booking.objects.filter(event_id=event_id, user_id=user_id).delete()
        if deleted == 0:
            return Response({"detail": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
