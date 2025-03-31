from typing import List, Tuple

from ecomm_platform.ordering.order import Order
from ecomm_platform.ordering.order_item import OrderItem

class OrderingPlatform:

    def create_order(self, customer_id: int, items: List[OrderItem]) -> Order:
        pass

    def modify_order(self, order_id: int, new_items: List[OrderItem]) -> None:
        pass

    def cancel_order(self, order_id: int) -> None:
        pass

    def complete_order(self, order_id: int) -> None:
        pass

    def track_order(self, order_id: int) -> str:
        pass

    def get_order_details(self, order_id: int) -> Order:
        pass

    def get_customer_orders(self, customer_id: int) -> List[Order]:
        pass