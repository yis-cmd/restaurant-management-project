from courses import Dish
from pydantic.dataclasses import dataclass

DEFAULT_TAX_PERCENT = 18
DEFAULT_TIP_PERCENT = 10

@dataclass
class BillDetails:
    price:float
    tip:float
    tax:float
    overall:float

class Bill:
    def __init__(self, meal:list[Dish], tax:float = DEFAULT_TAX_PERCENT, tip:float = DEFAULT_TIP_PERCENT) -> None:
        self.meal = meal
        self.tip = tip
        self.tax = tax
    def calc_price(self) -> float:
        return sum(dish.price for dish in self.meal)
    def calc_tax(self, price:float) -> float:
        return price * (self.tax / 100)
    def calc_tip(self, price:float) -> float:
        return price * (self.tip / 100)
    def overall(self)->BillDetails:
        price = self.calc_price()
        tip = self.calc_tip(price)
        tax = self.calc_tax(price + tip)
        overall = price + tip + tax
        return BillDetails(price, tip, tax, overall)