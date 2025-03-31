from typing import List, Optional, Tuple

from ecomm_platform.ordering.order import Order
from ecomm_platform.ordering.order_item import OrderItem
from ecomm_platform.shipping.shipment import Shipment
from ecomm_platform.shipping.shipping_label import ShippingLabel


customer_address: str
customer_id: int
customer_id: int
customer_name: str
destination_address: str
order_date: str
order_id: int
order_item_id: int
order_item_price: float
order_item_quantity: int
order_items: List[OrderItem]
order_status: str
shipment_id: int
shipping_cost: float
shipping_date: Optional[str]
shipping_label: Optional[ShippingLabel]
shipping_status: str
supplier_address: str
supplier_contact_info: str
supplier_id: int
supplier_id: int
supplier_item_id: int
supplier_item_price: float
supplier_name: str


def add_shipping_label(label: ShippingLabel) -> None:
    pass

def calculate_shipping_cost(order_id: int) -> float:
    pass

def calculate_total_cost() -> float:
    pass

# Notice that these two functions have the same name but different signatures
# The one that does not take an order_id has to be in the Order class
# so it can use self. The one that needs an order_id belongs in the
# OrderingPlatform class.
def cancel_order() -> None:
    pass

def cancel_order(order_id: int) -> None:
    pass

def complete_order(order_id: int) -> None:
    pass

def create_order(customer_id: int, items: List[OrderItem]) -> Order:
    pass

def create_shipment(order_id: int, destination_address: str) -> Shipment:
    pass

def get_customer_details() -> None:
    pass

def get_customer_orders() -> List[Order]:
    pass

def get_customer_orders(customer_id: int) -> List[Order]:
    pass

def get_order(self, order_id: int) -> Order:
        pass

def get_order_details(order_id: int) -> Order:
    pass

def get_order_status() -> str:
    pass

def get_supplier_details() -> None:
    pass

def manage_order(self, order: Order) -> None:
        pass

def modify_order(new_items: List[OrderItem]) -> None:
    pass

def modify_order(order_id: int, new_items: List[OrderItem]) -> None:
    pass

def place_order(supplier_item_id: int, quantity: int) -> None:
    pass

def price_order(supplier_item_id: int, quantity: int) -> float:
    pass

def ship_shipment(shipment_id: int) -> None:
    pass

def track_order(order_id: int) -> str:
    pass

def track_shipment(shipment_id: int) -> str:
    pass

def update_shipping_status(new_status: str) -> None:
    pass

def update_shipment_status(shipment_id: int, new_status: str) -> None:
    pass

def generate_shipping_label(shipment_id: int) -> ShippingLabel:
    pass

