from typing import List

from ecomm_platform.shipping.shipment import Shipment
from ecomm_platform.shipping.shipping_label import ShippingLabel

class ShippingPlatform:

    def create_shipment(self, order_id: int, destination_address: str) -> Shipment:
        pass

    def calculate_shipping_cost(self, order_id: int) -> float:
        pass

    def track_shipment(self, shipment_id: int) -> str:
        pass

    def update_shipment_status(self, shipment_id: int, new_status: str) -> None:
        pass

    def generate_shipping_label(self, shipment_id: int) -> ShippingLabel:
        pass

    def ship_shipment(self, shipment_id: int) -> None:
        pass