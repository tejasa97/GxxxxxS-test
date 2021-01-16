from rest_framework import serializers
from .models import DeliveryVehicleOrders


class DeliveryVehicleOrdersSerializer(serializers.ModelSerializer):

    vehicle_type = serializers.CharField(source='delivery_vehicle.vehicle_type.name')
    delivery_vendor_id = serializers.IntegerField(source='delivery_vehicle.delivery_vendor_id')
    list_order_ids_assigned = serializers.SerializerMethodField()

    def get_list_order_ids_assigned(self, obj):
        """Returns a list of the `order id`s of the assigned `Order`s
        """
        return [order.order_id for order in obj.orders.all()]

    class Meta:
        model = DeliveryVehicleOrders
        fields = ('vehicle_type', 'delivery_vendor_id', 'list_order_ids_assigned',)
        read_only_fields = ('vehicle_type', 'delivery_vendor_id', 'list_order_ids_assigned',)
