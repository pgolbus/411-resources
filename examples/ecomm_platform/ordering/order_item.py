class OrderItem:
    def __init__(self, itemID: int, quantity: int, price: float):
        self.itemID = itemID
        self.quantity = quantity
        self.price = price

    def calculate_total(self) -> float:
        pass
