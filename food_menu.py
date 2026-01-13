import courses
import exceptions
from courses import DishDetails, BreadMenu

ComponentName = (
    courses.FirstCourses |
    courses.MainCourses | 
    courses.Additionals | 
    courses.Deserts | 
    courses.Drinks | 
    courses.BreadMenu
)

class Menu:
    def __init__(self) -> None:
        self.bread = courses.BreadMenu()
        self.first_course = courses.FirstCourses(courses.FirstCourse)
        self.main_course = courses.MainCourses(courses.MainCourse)
        self.additional = courses.Additionals(courses.Additional)
        self.desert = courses.Deserts(courses.Desert)
        self.drink = courses.Drinks(courses.Drink)

    def add_dish(self, dish_details:DishDetails, component_name:str, quantity: int | None = None) -> None:
        component:ComponentName = self._get_menu_component(component_name)
        if isinstance(component, courses.BreadMenu):
            if quantity is None:
                raise ValueError("bread requires quantity")
            component.add_bread(dish_details, quantity)
        else:
            component.add(component.allowed_type(dish_details))

    def remove_dish(self, dish_name:str, component_name:str):
        component:ComponentName = self._get_menu_component(component_name)
        if isinstance(component, courses.BreadMenu):
            component.remove_bread(dish_name)
        else:
            component.remove(dish_name)

    def view_dishes(self, component_name:str):
        component = self._get_menu_component(component_name)
        output = str(component)
        empty_list_output = "there are no dishes in this menu"
        return output if output else empty_list_output

    def _get_menu_component(self, component_name):
        valid = {"bread",
        "first_course",
        "main_course",
        "additional",
        "desert",
        "drink"}
        if component_name not in valid:
            raise exceptions.SectionNotExistError
        return getattr(self, component_name)
    
    def get_dish_by_name(self, component_name, dish_name):
        component:ComponentName = self._get_menu_component(component_name)
        if isinstance(component, BreadMenu):
            return self.bread.get_bread_by_name(dish_name)
        else:
            return component.get_dish_by_name(dish_name)