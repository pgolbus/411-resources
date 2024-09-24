class Shipment:
    def __init__(self, shipmentID: int, orderID: int, destinationAddress: str, shippingCost: float):
        self.shipmentID = shipmentID
        self.orderID = orderID
        self.destinationAddress = destinationAddress
        self.shippingCost = shippingCost

    def create_shipment(self, orderID: int, destinationAddress: str):
        pass

    def calculate_cost(self, weight: float, distance: int) -> float:
        pass
