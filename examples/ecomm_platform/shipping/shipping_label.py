from dataclasses import dataclass

@dataclass
class ShippingLabel:
    label_id: int
    shipment_id: int
    label_creation_date: str
    tracking_number: str