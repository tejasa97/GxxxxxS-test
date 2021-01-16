from django.test import TestCase
from orders.models import Order, SlotDelivery
from django.urls import reverse
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

        url = reverse("assign_slot_orders", kwargs={"slot_number": 1})
        orders_api_data = generate_orders_data([30, 10, 20])
        expected_delivery_response_data = [
            {'vehicle_type': 'bike', 'delivery_vendor_id': 1, 'list_order_ids_assigned': [1]},
            {'vehicle_type': 'bike', 'delivery_vendor_id': 2, 'list_order_ids_assigned': [2, 3]}
        ]

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_delivery_response_data)

    def test_case_2(self):
        """Test a easy order combination [50, 50] for slot 1
        (OPTIMAL) uses 2 `scooters`
        """

        url = reverse("assign_slot_orders", kwargs={"slot_number": 1})
        orders_api_data = generate_orders_data([50, 50])
        expected_delivery_response_data = [
            {'vehicle_type': 'scooter', 'delivery_vendor_id': 1, 'list_order_ids_assigned': [1]},
            {'vehicle_type': 'scooter', 'delivery_vendor_id': 2, 'list_order_ids_assigned': [2]}
        ]

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_delivery_response_data)

    def test_case_3(self):
        """Test a easy order combination [50, 50] for slot 3
        (NOT OPTIMAL)
        Optimal soln should use 1 `truck`;  this uses 2 `scooters`
        """

        url = reverse("assign_slot_orders", kwargs={"slot_number": 3})
        orders_api_data = generate_orders_data([50, 50])
        expected_delivery_response_data = [
            {'vehicle_type': 'scooter', 'delivery_vendor_id': 1, 'list_order_ids_assigned': [1]},
            {'vehicle_type': 'scooter', 'delivery_vendor_id': 2, 'list_order_ids_assigned': [2]}
        ]

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_delivery_response_data)

    def test_case_4(self):
        """Test a easy order combination [30, 50] for slot 3
        (OPTIMAL) uses 1 `scooter` and a `bike`
        """

        url = reverse("assign_slot_orders", kwargs={"slot_number": 3})
        orders_api_data = generate_orders_data([30, 50])
        expected_delivery_response_data = [
            {'vehicle_type': 'scooter', 'delivery_vendor_id': 1, 'list_order_ids_assigned': [2]},
            {'vehicle_type': 'bike', 'delivery_vendor_id': 1, 'list_order_ids_assigned': [1]}
        ]

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_delivery_response_data)

    def test_case_5(self):
        """Test a easy order combination [30, 10, 50] for slot 3
        (NOT OPTIMAL) 
        Optimal soln should use 2 `scooters`; this uses 1 `scooter` and 2 `bikes`
        """

        url = reverse("assign_slot_orders", kwargs={"slot_number": 3})
        orders_api_data = generate_orders_data([30, 10, 50])
        expected_delivery_response_data = [
            {'vehicle_type': 'scooter', 'delivery_vendor_id': 1, 'list_order_ids_assigned': [3]},
            {'vehicle_type': 'bike', 'delivery_vendor_id': 1, 'list_order_ids_assigned': [1]},
            {'vehicle_type': 'bike', 'delivery_vendor_id': 2, 'list_order_ids_assigned': [2]}
        ]

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_delivery_response_data)

    def test_case_6(self):
        """Test slight complex cases
        (NOT OPTIMAL)
        Optimal soln is [scooter, scooter]
        """

        url = reverse("assign_slot_orders", kwargs={"slot_number": 1})
        orders_api_data = generate_orders_data([10, 20, 30, 40])
        expected_delivery_response_data = [
            {'vehicle_type': 'scooter', 'delivery_vendor_id': 1, 'list_order_ids_assigned': [1, 4]},
            {'vehicle_type': 'bike', 'delivery_vendor_id': 1, 'list_order_ids_assigned': [3]},
            {'vehicle_type': 'bike', 'delivery_vendor_id': 2, 'list_order_ids_assigned': [2]}
        ]

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_delivery_response_data)
        # note that, optimal soln is [scooter, scooter]

    def test_case_7(self):
        """Test easy order combination [30, 10, 50] for slot 4
        (OPTIMAL) Optimal soln is [truck]
        """

        url = reverse("assign_slot_orders", kwargs={"slot_number": 4})
        orders_api_data = generate_orders_data([30, 10, 50])
        expected_delivery_response_data = [
            {'vehicle_type': 'truck', 'delivery_vendor_id': 1,
                'list_order_ids_assigned': [1, 2, 3]},
        ]

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_delivery_response_data)

    def test_case_8(self):
        """Test easy order combination [95, 5] for slot 2
        (OPTIMAL) Optimal soln is [truck]
        """

        url = reverse("assign_slot_orders", kwargs={"slot_number": 4})
        orders_api_data = generate_orders_data([95, 5])
        expected_delivery_response_data = [
            {'vehicle_type': 'truck', 'delivery_vendor_id': 1,
                'list_order_ids_assigned': [1, 2]},
        ]

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_delivery_response_data)

    def test_case_9(self):
        """Test easy order combination [30, 10, 20, 40] for slot 2
        (NON OPTIMAL) Optimal soln is [scooter, scooter]; obtained is [scooter, bike, bike]
        """

        url = reverse("assign_slot_orders", kwargs={"slot_number": 2})
        orders_api_data = generate_orders_data([30, 10, 20, 40])
        expected_delivery_response_data = \
            [
                {'vehicle_type': 'scooter', 'delivery_vendor_id': 1,
                    'list_order_ids_assigned': [2, 4]},
                {'vehicle_type': 'bike', 'delivery_vendor_id': 1, 'list_order_ids_assigned': [1]},
                {'vehicle_type': 'bike', 'delivery_vendor_id': 2, 'list_order_ids_assigned': [3]}
            ]

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_delivery_response_data)

    def test_case_10(self):
        """Test easy order combination [30, 10, 20, 40] for slot 4
        (OPTIMAL) Optimal soln is [truck]
        """

        url = reverse("assign_slot_orders", kwargs={"slot_number": 4})
        orders_api_data = generate_orders_data([30, 10, 20, 40])
        expected_delivery_response_data = [
            {'vehicle_type': 'truck', 'delivery_vendor_id': 1,
                'list_order_ids_assigned': [1, 2, 3, 4]},
        ]

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_delivery_response_data)

    def test_case_11(self):
        """Test easy order combination [10, 10, 10, 5, 5, 2, 1, 2, 25] for slot 3
        (NON OPTIMAL) Optimal soln is [truck] (or is it???); obtained is [bike, bike, bike]
        """

        url = reverse("assign_slot_orders", kwargs={"slot_number": 3})
        orders_api_data = generate_orders_data([10, 10, 10, 5, 5, 2, 1, 2, 25])
        expected_delivery_response_data = \
            [
                {'vehicle_type': 'bike', 'delivery_vendor_id': 1,
                    'list_order_ids_assigned': [4, 9]},
                {'vehicle_type': 'bike', 'delivery_vendor_id': 2,
                    'list_order_ids_assigned': [1, 2, 3]},
                {'vehicle_type': 'bike', 'delivery_vendor_id': 3,
                    'list_order_ids_assigned': [5, 6, 7, 8]}
            ]

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_delivery_response_data)

    def test_invalid_orders_weight(self):
        """Test exception arises if sum of order weights exceeds 100
        """

        url = reverse("assign_slot_orders", kwargs={"slot_number": 1})
        orders_api_data = generate_orders_data([10, 20, 30, 40, 50])

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")
        expected_error_response_data = {
            'detail': 'Order weights exceeds limit (100 kgs)'
        }

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_error_response_data)

    def test_invalid_slot_number(self):
        """Test exception arises if an invalid slot number is used
        """

        # use slot number 7
        url = reverse("assign_slot_orders", kwargs={"slot_number": 7})
        orders_api_data = generate_orders_data([10, 20, 30, 40])

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")
        expected_error_response_data = {
            'detail': 'Invalid Slot number provided'
        }

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_error_response_data)

    def test_invalid_order_weight(self):
        """Test exception arises if an object whose weight is more than capacity of any available delivery vehicle is requested
        """

        # use slot number 7
        url = reverse("assign_slot_orders", kwargs={"slot_number": 1})
        orders_api_data = generate_orders_data([10, 20, 60])

        response = self.client.post(url, data=json.dumps(
            orders_api_data), content_type="application/json")
        expected_error_response_data = {
            'detail': 'Unable to assign to the available delivery vehicles'
        }

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_error_response_data)
