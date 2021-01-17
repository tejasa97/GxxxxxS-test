from django.db import models
from .managers import AscendingOrderManager
from .utils import BaseModel


class VehicleType(BaseModel):
    """Class that represents a vehicle type
    eg : bike, scooter, truck
    """

    name = models.CharField(null=False, max_length=10)
    vehicle_capacity = models.IntegerField(null=False)

    @staticmethod
    def get_delivery_vehicles_available(vehicles):
        """Returns all delivery vehicles available for the `VehicleType` queryset

        :param vehicles: QuerySet(`VehicleType`)
        :type vehicles: QuerySet
        :return: list of available delivery vehicles
        :rtype: List[`DeliveryVehicle`]
        """

        available_delivery_vehicles = []
        for vehicle_type in vehicles:
            available_delivery_vehicles.extend(
                DeliveryVehicle.objects.filter(vehicle_type=vehicle_type).all()
            )

        return available_delivery_vehicles


class Slot(BaseModel):
    """Class that represents a time range Slot
    eg : `6-9` hrs, `9-13` hrs
    """

    class InvalidSlotNumber(Exception):
        """Raised if an invalid slot number is provided
        """
        ...

    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4

    # Hard code the slot numbers and their time ranges
    SLOT_CHOICES = (
        (FIRST, '6-9'),
        (SECOND, '9-13'),
        (THIRD, '16-19'),
        (FOURTH, '19-23'),
    )

    slot_number = models.PositiveSmallIntegerField(choices=SLOT_CHOICES, default=None, null=False)
    slot_start_time = models.TimeField(null=True)
    slot_end_time = models.TimeField(null=True)

    vehicle_types_assigned = models.ManyToManyField(VehicleType)

    @classmethod
    def get_vehicle_types_assigned(cls, slot_number):
        """Returns the vehicle types assigned for `slot_number`
        Returns in ascending order of `vehicle_capacity`

        :param slot_number: Slot number
        :type slot_number: int
        :raises InvalidSlotNumber: raised if an invalid slot number is provided
        :return: vehicles
        :rtype: QuerySet(VehicleType)
        """
        try:
            slot = cls.objects.get(slot_number=slot_number)
        except cls.DoesNotExist:
            raise cls.InvalidSlotNumber

        return slot.vehicle_types_assigned.order_by('vehicle_capacity').all()


class SlotDelivery(BaseModel):
    """Class that represents a Delivery fleet responding for a orders request for a `Slot`
    """

    class InvalidSlotNumber(Exception):
        """Raised if the invalid slot number is provided
        """
        ...

    class CannotAssignOrders(Exception):
        """Raised if the system is unable to assign the given orders for delivery
        """
        ...

    class OrdersWeightLimitError(Exception):
        """Raised if the sum of the orders' weight exceeds limit
        """
        ...

    slot_id = models.ForeignKey(Slot, on_delete=models.CASCADE)

    vehicles_assigned = models.BooleanField(null=True)
    created = models.DateTimeField(auto_now_add=True)  # used to identify on which date?

    @classmethod
    def assign_new_batch_order_delivery(cls, slot_number, orders):
        """Assigns a `DeliveryVehicleOrders` fleet for the provided orders and slot number
        Currently uses the `First Fit Decreasing Bin Packing algorithm` to assign the delivery vehicles

        links : 
        # https://www.youtube.com/watch?v=GbPmmZQHQo8,
        # https://www.geeksforgeeks.org/bin-packing-problem-minimize-number-of-used-bins

        :param slot_num: slot number
        :type slot_num: int
        :param orders: list of orders
        :type orders: dict
        :return: list of `DeliveryVehicleOrders` objects
        :rtype: List[`DeliveryVehicleOrders`]
        """

        # Get the order objects
        try:
            orders = Order.bulk_create_from_dict(orders)
        except Order.WeightLimitExceeded:
            raise cls.OrdersWeightLimitError

        # Initialize a new `SlotDelivery`
        try:
            slot = Slot.objects.get(slot_number=slot_number)
        except Slot.DoesNotExist:
            raise cls.InvalidSlotNumber
        slot_delivery = cls.objects.create(slot_id=slot)

        """ Now, the CRUX... Assign the delivery vehicles! """
        available_vehicle_types = Slot.get_vehicle_types_assigned(
            slot_number=slot_number)  # vehicle types available for the slot
        available_delivery_vehicles = VehicleType.get_delivery_vehicles_available(
            available_vehicle_types)  # all delivery vehicles available for the slot

        return cls.assign_first_fit_delivery(
            available_delivery_vehicles, orders, slot_delivery)

    @classmethod
    def assign_first_fit_delivery(cls, available_delivery_vehicles, orders, slot_delivery):
        """Assigns the delivery vehicles with the First Fit Decreasing algorithm

        :param available_delivery_vehicles: available `DeliveryVehicle` objects
        :type available_delivery_vehicles: List[`DeliveryVehicle`]
        :param orders: `Order` objects
        :type orders: List[`Order`]
        :param slot_delivery: `SlotDelivery` object
        :raises cls.CannotAssignOrders: raised if there exists an order which cannot be assigned to any vehicle
        :return: `DeliveryVehicleOrder` objects
        :rtype: List[`DeliveryVehicleOrder`]
        """

        delivery_vehicles_assigned = []
        # Go through orders in descending order of their weight
        for order in sorted(orders, key=lambda x: x.weight, reverse=True):
            order_added = False

            for delivery_vehicle in delivery_vehicles_assigned:
                if order.weight <= delivery_vehicle.capacity:
                    delivery_vehicle.add_order(order)
                    order_added = True
                    break

            if order_added == False:
                # Assign a new delivery vehicle
                for idx, vehicle in enumerate(available_delivery_vehicles):

                    if vehicle.max_capacity >= order.weight:
                        delivery_vehicle = available_delivery_vehicles.pop(idx)
                        new_delivery_vehicle_assigned = delivery_vehicle.assign_vehicle(
                            slot_delivery=slot_delivery)
                        new_delivery_vehicle_assigned.add_order(order)

                        delivery_vehicles_assigned.append(new_delivery_vehicle_assigned)
                        order_added = True
                        break

            # if the orders just cannot be assigned
            if order_added is False:
                raise cls.CannotAssignOrders

        return delivery_vehicles_assigned

    @classmethod
    def assign_best_fit_delivery(cls, available_delivery_vehicles, orders, slot_delivery):
        """Assigns the delivery vehicles with the Best Fit Decreasing algorithm

        :param available_delivery_vehicles: available `DeliveryVehicle` objects
        :type available_delivery_vehicles: List[`DeliveryVehicle`]
        :param orders: `Order` objects
        :type orders: List[`Order`]
        :param slot_delivery: `SlotDelivery` object
        :raises cls.CannotAssignOrders: raised if there exists an order which cannot be assigned to any vehicle
        :return: `DeliveryVehicleOrder` objects
        :rtype: List[`DeliveryVehicleOrder`]
        """

        delivery_vehicles_assigned = []
        # Go through orders in descending order of their weight
        for order in sorted(orders, key=lambda x: x.weight, reverse=True):
            order_added = False

            if len(delivery_vehicles_assigned) > 0:
                min_remainder = 101
                best_fit_vehicle = None
                for delivery_vehicle in delivery_vehicles_assigned:
                    fit_metric = delivery_vehicle.capacity - order.weight

                    if fit_metric < 0:
                        continue
                    if fit_metric < min_remainder:
                        min_remainder = fit_metric
                        best_fit_vehicle = delivery_vehicle

                # If best fit vehicle found, add the order to it
                if best_fit_vehicle is not None:
                    best_fit_vehicle.add_order(order)
                    order_added = True

            if order_added == False:
                # Assign a new delivery vehicle
                for idx, vehicle in enumerate(available_delivery_vehicles):

                    if vehicle.max_capacity >= order.weight:
                        delivery_vehicle = available_delivery_vehicles.pop(idx)
                        new_delivery_vehicle_assigned = delivery_vehicle.assign_vehicle(
                            slot_delivery=slot_delivery)
                        new_delivery_vehicle_assigned.add_order(order)

                        delivery_vehicles_assigned.append(new_delivery_vehicle_assigned)
                        order_added = True
                        break

            # if the orders just cannot be assigned
            if order_added is False:
                raise cls.CannotAssignOrders

        return delivery_vehicles_assigned


class DeliveryVehicle(BaseModel):
    """Class that represents a Delivery Partner's `Delivery Vehicle`
    It can either be any vehicle type from `VehicleType`
    """

    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    delivery_vendor_id = models.PositiveIntegerField()

    @property
    def max_capacity(self):
        """Returns the maximum weight capacity of the delivery vehicle

        :return: max capacity
        :rtype: int
        """

        return self.vehicle_type.vehicle_capacity

    def assign_vehicle(self, slot_delivery):
        """Returns a new instance of `DeliveryVehicleOrders` to cater to this `SlotDelivery`

        :param slot_delivery: `SlotDelivery` object
        :return: new `DeliveryVehicleOrders` object
        """

        return DeliveryVehicleOrders.objects.create(delivery_vehicle=self, slot_delivery=slot_delivery)

    def __str__(self):
        return f"DeliveryVehicle <VehicleType: {self.vehicle_type.name}, DeliveryVendorID: {self.delivery_vendor_id}>"

    def __repr__(self):
        return self.__str__()


class DeliveryVehicleOrders(BaseModel):
    """Class that represents a `DeliveryVehicle` used in a delivery, along with the `Order`s it carries
    """

    delivery_vehicle = models.ForeignKey(DeliveryVehicle, on_delete=models.CASCADE)
    slot_delivery = models.ForeignKey(SlotDelivery, on_delete=models.CASCADE,
                                      related_name='delivery_vehicle_orders', null=False)

    def __init__(self, *args, **kwargs):
        """Adds an attr `capacity` to help keep track of its current capacity
        """

        super().__init__(*args, **kwargs)
        self.capacity = self.delivery_vehicle.max_capacity

    @property
    def vehicle_type(self):
        """Returns the vehicle's `VehicleType`

        :return: `VehicleType` object
        """

        return self.delivery_vehicle.vehicle_type

    def add_order(self, order):
        """Adds an `Order` to the vehicle

        :param order: `Order` object
        """

        self.orders.add(order, bulk=False)
        self.capacity -= order.weight

        self.save()

    def __str__(self):
        return f"DeliveryVehicleOrder <ID : {self.delivery_vehicle}, orders : {[order for order in self.orders.all()]}>"

    def __repr__(self):
        return self.__str__()


class Order(BaseModel):
    """Class that represents an Order
    Also stores the `DeliveryVehicleOrder` instance that delivered it
    """

    class WeightLimitExceeded(Exception):
        """Raised if order weights exceeds limit
        """
        ...

    order_id = models.PositiveIntegerField(null=False)
    weight = models.FloatField(null=False)

    delivery_vehicle_order = models.ForeignKey(
        DeliveryVehicleOrders, on_delete=models.CASCADE, related_name='orders', null=True)

    objects = AscendingOrderManager()

    @classmethod
    def bulk_create_from_dict(cls, orders_list):
        """Bulk creates orders from a dict

        :param orders_list: dict
        :type orders_list: List[dict]
        :return: list of `Order`s
        :rtype: List[`Order`]
        """

        orders_data = [
            cls(order_id=order['order_id'],
                weight=order['order_weight']
                )
            for order in orders_list
        ]

        if sum(order.weight for order in orders_data) > 100:
            raise cls.WeightLimitExceeded

        return cls.objects.bulk_create(orders_data)

    def __str__(self):
        return f"Order <order_id {self.order_id}, weight: {self.weight}>"

    def __repr__(self):
        return self.__str__()
