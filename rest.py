from __future__ import annotations
import tables
import reservation
import food_menu
from datetime import timedelta
import exceptions

DEFAULT_MIN_MEAL_TIME = 30
 
class Restaurant:
    def __init__(self, name, min_meal_time:timedelta = timedelta(minutes = DEFAULT_MIN_MEAL_TIME)) -> None:
        self.name = name
        self.menu = food_menu.Menu()
        self.tables = tables.Tables()
        self.reservations = reservation.Reservations(self.tables, self.menu)
        self.min_meal_time = min_meal_time
    def __str__(self) -> str:
        return f"{self.name}"

class Restaurants:
    def __init__(self) -> None:
        self.collection:list[Restaurant] = []
    def _create_restaurant(self, name):
        return Restaurant(name)
    def add_restaurant(self, name):
        if name not in [r.name for r in self.collection]:
            self.collection.append(self._create_restaurant(name))
        else:
            raise exceptions.RestaurantAlreadyExistsError
    def delete_restaurant_by_name(self, name:str) -> None:
        restaurant = self.get_restaurant_by_name(name)
        self.collection.remove(restaurant)
           
    def __str__(self) -> str:
        if len(self.collection) == 0:
            return "\nthere are no restaurants at the moment"
        lines = [f" {i}. {rest}" for i, rest in enumerate(self.collection, start = 1)]
        return "restaurants list:\n" + "\n".join(lines)
    def get_restaurant_by_name(self, name):
        try:
            return next(r for r in self.collection if r.name == name)
        except StopIteration:
            raise exceptions.RestaurantNotExistError

if __name__ == "__main__":
    pass