from typing import List

from ecomm_platform.ordering.ordering.order import Order

class Customer:
    def __init__(self,
                 customer_id: int,
                 customer_name: str,
                 customer_address: str) -> None:
        pass

    def get_customer_details(self) -> None:
        pass

    def get_customer_orders(self) -> List[Order]:
        pass

    def get_order(self, order_id: int) -> Order:
        pass

    def manage_order(self, order: Order) -> None:
        pass