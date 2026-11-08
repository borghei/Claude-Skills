from dataclasses import dataclass


@dataclass
class Order:
    sku: str
    quantity: int
