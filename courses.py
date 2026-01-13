import exceptions
from pydantic.dataclasses import dataclass
from enum import Enum

ADDITION_FOR_COLD_DRINK = 10
ADDITION_FOR_MEDIUM_DRINK = 15
ADDITION_FOR_LARGE_DRINK = 30

@dataclass
class DishDetails:
    name:str
    price:float
    description:str

class Dish:
    def __init__(self, dish_details:DishDetails, dish_id:int | None = None) -> None:
        self.name = dish_details.name
        self.base_price = dish_details.price
        self.description = dish_details.description
        self.id = dish_id
    @property
    def price(self):
        return self.base_price

    def __str__(self) -> str:
        return f"{self.name}, costs: {self.base_price}, description {self.description}\n"
    
class MenuSection:
    def __init__(self,allowed_type) -> None:
        self.allowed_type = allowed_type
        self.items:list[Dish] = []
    def __str__(self) -> str:
        return "".join([str(item) for item in self.items])
    def add(self, item):
        if not isinstance(item, self.allowed_type):
            raise TypeError
        self.items.append(item)
    def get_dish_by_name(self, name):
        try:
            return next(dish for dish in self.items if dish.name == name)
        except StopIteration:
            raise exceptions.DishNotExistError
    def remove(self, name):
        dish = self.get_dish_by_name(name)
        self.items.remove(dish)
       
class FirstCourse(Dish):
    pass
class FirstCourses(MenuSection):
    def __init__(self, allowed_type) -> None:
        super().__init__(allowed_type)
        self.allowed_type = FirstCourse

class MainCourse(Dish):
    pass
class MainCourses(MenuSection):
    def __init__(self, allowed_type) -> None:
        super().__init__(allowed_type)
        self.allowed_type = MainCourse

class Additional(Dish):
    pass
class Additionals(MenuSection):
    def __init__(self, allowed_type) -> None:
        super().__init__(allowed_type)
        self.allowed_type = Additional
    
class Desert(Dish):
    def __init__(self, dish_details: DishDetails, dish_id: int | None = None) -> None:
        super().__init__(dish_details, dish_id)
        self.base_price = dish_details.price
class Deserts(MenuSection):
    def __init__(self, allowed_type) -> None:
        super().__init__(allowed_type)
        self.allowed_type = Desert

class ClientDesert(Desert):
    def __init__(self, base:Desert, with_sugar:bool) -> None:
        super().__init__(DishDetails(base.name, base.base_price, base.description))
        self.with_sugar = with_sugar
    @property
    def price(self) ->float:
        with_sugar_options = {True : 0, False : 10}
        addition = with_sugar_options[self.with_sugar]
        return self.base_price * (1 + addition / 100)

class Drink(Dish):
    def __init__(self, dish_details: DishDetails, dish_id: int | None = None) -> None:
        super().__init__(dish_details, dish_id)
        self.base_price = dish_details.price
class Drinks(MenuSection):
    def __init__(self, allowed_type) -> None:
        super().__init__(allowed_type)
        self.allowed_type = Drink

class DrinkSizes(Enum):
    SMALL = "s"
    MEDIUM = "m"
    LARGE = "l"

class ClientDrink(Drink):
    def __init__(self, base:Drink, is_cold:bool, size:DrinkSizes) -> None:
        super().__init__(DishDetails(base.name, base.base_price, base.description))
        self.is_cold = is_cold
        self.size = size
    @property
    def price(self):
        is_cold_options = {True : ADDITION_FOR_COLD_DRINK, False : 0}
        size_options = {
            DrinkSizes.SMALL : 0, 
            DrinkSizes.MEDIUM : ADDITION_FOR_MEDIUM_DRINK, 
            DrinkSizes.LARGE : ADDITION_FOR_LARGE_DRINK
            }
        sum_up_addition = is_cold_options[self.is_cold] + size_options[self.size]
        return self.base_price * (1 + sum_up_addition / 100)

class Bread(Dish):
    pass

class BreadInventory:
    def __init__(self, dish_details:DishDetails, quantity:int) -> None:
        self.bread = Bread(DishDetails(dish_details.name, dish_details.price, dish_details.description))
        self.quantity = quantity

class BreadMenu:
    def __init__(self) -> None:
        self.menu:list[BreadInventory] = []

    def add_bread(self, dish_details:DishDetails, quantity:int):
        for bread_inventory in self.menu:
            if bread_inventory.bread.name == dish_details.name:
                bread_inventory.quantity += quantity
                return
        self.menu.append(BreadInventory(dish_details, quantity))

    def remove_bread(self, name):
        bread = self.get_bread_by_name(name)
        self.menu.remove(bread)

    def get_bread_by_name(self, name) -> BreadInventory:
        try:
            return next(bread for bread in self.menu if bread.bread.name == name)
        except StopIteration:
            raise exceptions.DishNotExistError
        
    def order_bread(self, bread:BreadInventory) -> Bread:
        self.sell_bread(bread)
        return bread.bread
        
    def sell_bread(self, bread:BreadInventory):
        for bread_inventory in self.menu:
            if bread_inventory == bread:
                if bread_inventory.quantity == 0:
                    raise exceptions.NotEnoughBreadError
                bread_inventory.quantity -= 1
                return None
        raise exceptions.DishNotExistError
    
    def __str__(self) -> str:
        breads = []
        for i in self.menu:
            if i.quantity > 0:
                breads.append(f"{i.bread.name} costs {i.bread.price} {i.quantity} in stock\n")
        return "".join(breads)