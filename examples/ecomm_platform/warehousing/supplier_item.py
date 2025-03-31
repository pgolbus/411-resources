from dataclasses import dataclass

@dataclass
class SupplierItem:
    supplier_id: int
    supplier_item_id: int
    supplier_item_price: float