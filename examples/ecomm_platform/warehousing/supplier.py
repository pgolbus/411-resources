class Supplier:
    def __init__(self, supplierID: int, name: str, contactInfo: str):
        self.supplierID = supplierID
        self.name = name
        self.contactInfo = contactInfo

    def place_order(self, itemID: int, quantity: int):
        pass

    def get_supplier_details(self, supplierID: int):
        pass