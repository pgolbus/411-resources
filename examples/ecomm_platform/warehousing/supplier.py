class Supplier:
    def __init__(self,
                 supplier_id: int,
                 supplier_name: str,
                 supplier_address: str,
                 supplier_contact_info: str) -> None:
        pass

    def price_order(self, supplier_item_id: int, quantity: int) -> float:
        pass

    def place_order(self, supplier_item_id: int, quantity: int) -> None:
        pass

    def get_supplier_details(self) -> None:
        pass
