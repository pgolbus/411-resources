from typing import List

from ecomm_platform.ordering.order_item import OrderItem

class Order:
    def __init__(self, orderID: int, customerID: int, orderDate: str, orderStatus: str):
        self.orderID = orderID
        self.customerID = customerID
        self.orderDate = orderDate
        self.orderStatus = orderStatus

    def create_order(self, customerID: int, items: List['OrderItem']):
        pass

    def modify_order(self, orderID: int, new_items: List['OrderItem']):
        pass

    def cancel_order(self, orderID: int):
        pass