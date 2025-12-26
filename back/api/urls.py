from rest_framework.routers import DefaultRouter
from .views import EventViewSet, BookingViewSet

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="events")
router.register(r"bookings", BookingViewSet, basename="bookings")

urlpatterns = [] + router.urls
