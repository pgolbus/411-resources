from typing import List

from ecomm_platform.ordering.order_item import OrderItem

class Order:
    def __init__(self,
                 order_id: int,
                 customer_id: int,
                 order_date: str,
                 order_status: str,
                 order_items: List[OrderItem]) -> None:
        self.order_id = order_id
        self.customer_id = customer_id
        self.order_date = order_date
        self.order_status = order_status
        self.order_items = order_items

    def modify_order(self, new_items: List[OrderItem]) -> None:
        pass

    def cancel_order(self) -> None:
        pass

    def get_order_status(self) -> str:
        pass

    def calculate_total_cost(self) -> float:
        pass
