from django.test import TestCase
from orders.models import Order, SlotDelivery, VehicleType, Slot
import json


def generate_orders_data(weights_list):

    return [{"order_id": idx, "order_weight": weight} for idx, weight in enumerate(weights_list, 1)]


class DeliveryTestCases(TestCase):
    def setUp(self):
        pass

    def test_case_1(self):
        """Test a easy order combination [30, 10, 20] for slot 1
        (OPTIMAL) uses 2 `bikes`
        This is the test case provided as an example in the Assignment Document
        """

        orders_data = generate_orders_data([30, 10, 20])
        assigned_delivery_vehicles = SlotDelivery.assign_new_batch_order_delivery(
            slot_number=1, orders=orders_data)

        bike = VehicleType.objects.get(name='bike')
        self.assertEqual(len(assigned_delivery_vehicles), 2)  # 2 vehicles
        self.assertEqual(
            sum(dv.vehicle_type == bike for dv in assigned_delivery_vehicles), 2
        )  # 2 bike

    def test_case_2(self):
        """Test a easy order combination [50, 50] for slot 1
        (OPTIMAL) uses 2 `scooters`
        """

        orders_data = generate_orders_data([50, 50])
        assigned_delivery_vehicles = SlotDelivery.assign_new_batch_order_delivery(
            slot_number=1, orders=orders_data)

        scooter = VehicleType.objects.get(name='scooter')
        self.assertEqual(len(assigned_delivery_vehicles), 2)  # 2 vehicles
        self.assertEqual(
            sum(dv.vehicle_type == scooter for dv in assigned_delivery_vehicles), 2
        )  # 2 scooters

    def test_get_vehicle_types_for_invalid_slot_number(self):
        """Test that appropriate exception is raised when an invalid slot number is used (eg : slot number = 9)
        """

        self.assertRaises(Slot.InvalidSlotNumber, Slot.get_vehicle_types_assigned, slot_number=6)

    def test_orders_weight_limit_error(self):
        """Test that approriate exception is raised when the sum of orders exceeds the limit set (in this case: 100kg)
        """

        order_weights = [30, 30, 40, 40, 40, 50, 50]
        orders_data = generate_orders_data(order_weights)

        self.assertRaises(SlotDelivery.OrdersWeightLimitError,
                          SlotDelivery.assign_new_batch_order_delivery, slot_number=1, orders=orders_data)
