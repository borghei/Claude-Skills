# Deliberate layer violation: infrastructure reaching up into presentation
from controllers.order_controller import OrderController
from models.order import Order


class OrderRepository:
    def save(self, order: Order) -> Order:
        return order
