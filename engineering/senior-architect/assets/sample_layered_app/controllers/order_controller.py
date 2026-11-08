from services.order_service import OrderService


class OrderController:
    def __init__(self):
        self.service = OrderService()

    def create(self, payload):
        return self.service.place_order(payload)
