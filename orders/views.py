from django.shortcuts import render
from rest_framework import serializers
from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import SlotDelivery
from .serializers import DeliveryVehicleOrdersSerializer


class AssignSlotOrders(APIView):

    permission_classes = (AllowAny,)

    class InputSerializer(serializers.Serializer):

        order_id = serializers.IntegerField(allow_null=False)
        order_weight = serializers.IntegerField(allow_null=False)

    def post(self, request, slot_number, *args, **kwargs):
        """View to post a new Orders Delivery request

        :param request: Django request object
        :param slot_number: slot number
        :type slot_number: int
        :return: JSON response
        """

        serializer = self.InputSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        try:
            assigned_delivery_vehicle_orders = SlotDelivery.assign_new_batch_order_delivery(
                slot_number=slot_number, orders=serializer.validated_data)
        except SlotDelivery.OrdersWeightLimitError:
            raise exceptions.ParseError("Order weights exceeds limit (100 kgs)")
        except SlotDelivery.InvalidSlotNumber:
            raise exceptions.ParseError("Invalid Slot number provided")
        except SlotDelivery.CannotAssignOrders:
            raise exceptions.ParseError("Unable to assign to the available delivery vehicles")

        serialized_response = DeliveryVehicleOrdersSerializer(
            assigned_delivery_vehicle_orders, many=True)

        return Response(serialized_response.data)
