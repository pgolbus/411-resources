from typing import Optional

from ecomm_platform.shipping.shipping_label import ShippingLabel

class Shipment:
    def __init__(self,
                 shipment_id: int,
                 order_id: int,
                 destination_address: str,
                 shipping_cost: float,
                 shipping_status: str,
                 shipping_date: Optional[str] = None,
                 shipping_label: Optional[ShippingLabel] = None) -> None:
        pass

    def update_shipping_status(self, new_status: str) -> None:
        pass

    def add_shipping_label(self, label: ShippingLabel) -> None:
        pass