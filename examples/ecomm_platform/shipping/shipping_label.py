class ShippingLabel:
    def __init__(self, labelID: int, shipmentID: int, trackingNumber: str):
        self.labelID = labelID
        self.shipmentID = shipmentID
        self.trackingNumber = trackingNumber

    def generate_label(self, shipmentID: int):
        pass
