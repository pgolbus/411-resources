from typing import List, Tuple

customer_address: str
customer_id: int
customer_name: str
destination_address: str
item_id: int
item_price: float
item_quantity: int
label_creation_date: str
order_date: str
order_id: int
order_status: str
shipment_id: int
shipping_cost: float
shipping_date: str
shipping_label_id: int
supplier_address: str
supplier_id: int
supplier_name: str
tracking_number: str

def create_order(customer_id: int, items: List[Item]) -> None:
  pass

def modify_order(order_id: int, new_items: List[Item]) -> None:
  pass

def cancel_order(order_id: int) -> None:
  pass

def calculate_shipping_cost(order_id: int) -> float:
  pass

def calculate_total_cost(order_id: int) -> float:
  pass

def track_order(order_id: int) -> str:
  pass

def get_order_status(order_id: int) -> str:
  pass

def get_order_details(order_id: int) -> Order:
  pass

def get_customer_orders(customer_id: int) -> List[Order]:
  pass

def get_supplier_orders(supplier_id: int) -> List[Order]:
  pass

def get_customer_details(customer_id: int) -> Tuple(str, str):
  pass






