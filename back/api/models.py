from django.db import models
from django.contrib.auth import get_user_model


UserModel = get_user_model()

class Event(models.Model):
    name = models.CharField(max_length=255)
    total_seats = models.IntegerField()

    def __str__(self):
        return self.name


class Booking(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bookings", verbose_name="Мероприятие")
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["event", "user_id"], name="uniq_booking_per_user_event"),
        ]
        indexes = [
            models.Index(fields=["event"]),
            models.Index(fields=["event", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event}:{self.user.get_full_name()}"
