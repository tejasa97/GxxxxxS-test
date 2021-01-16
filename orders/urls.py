from .views import AssignSlotOrders
from django.urls import path

urlpatterns = [
    path('assign-slot-orders/<int:slot_number>', AssignSlotOrders.as_view(), name="assign_slot_orders")
]
