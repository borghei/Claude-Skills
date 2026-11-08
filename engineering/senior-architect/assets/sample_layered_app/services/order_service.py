from repositories.order_repository import OrderRepository
from models.order import Order


class OrderService:
    def __init__(self):
        self.repo = OrderRepository()

    def place_order(self, payload):
        return self.repo.save(Order(**payload))
