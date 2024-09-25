from dataclasses import dataclass

@dataclass
class OrderItem:
    order_item_id: int
    order_item_quantity: int
    order_item_price: float
