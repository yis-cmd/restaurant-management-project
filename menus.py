from collections.abc import Callable
import sys
from rest import Restaurants, Restaurant
from reservation import ReservationDetails, Reservation, Reservations
from tables import Tables
from app_io import AppIO
import food_menu
from courses import DishDetails, Dish, BreadInventory, Bread, ClientDesert, ClientDrink, DrinkSizes
from bill import Bill, BillDetails
import exceptions

SIZE_MAP = {
            "s":DrinkSizes.SMALL,
            "m":DrinkSizes.MEDIUM,
            "l":DrinkSizes.LARGE
        }

class Menu:
    def __init__(self, title:str) -> None:
        self.title = title
        self.options:dict[str, tuple[str, Callable]] = {}
        

    def add_back_key(self):
        self.add_option("/q", "go back", self.go_back)

    def add_option(self, key:str, text:str, action:Callable) -> None:
        self.options[key] = (text, action)

    def show(self) -> None:
        print(f"\n=== {self.title} ===")
        for key, (text,_) in self.options.items():
            print(f"{key}: {text}")

    def get_choice(self) -> str:
        choice = input("> ").strip().casefold()
        while choice not in self.options:
            print("invaid key! try again")
            choice = input("> ").strip().casefold()
        return choice

    def run(self) -> None:
        try:
            while True:
                self.show()
                choice = self.get_choice()
                self.options[choice][1]()
        except exceptions.BackMenu:
            return
    
    def go_back(self) -> None:
        raise exceptions.BackMenu
    
class MainMenu(Menu):
    def __init__(self, title: str, restaurants:Restaurants) -> None:
        super().__init__(title)
        self.restaurants = restaurants
        self.io = AppIO()
        self.add_option("ml", "manage restaurant list", lambda : ManageRestListMenu("manage restaurant list", restaurants).run())
        self.add_option("me", "manage and existing restaurant", self.redirect_to_rest)
        self.add_option("quit", "exit", self.do_exit)

    def redirect_to_rest(self):
        try:
            name = self.io.get_name("enter your restaurant name")
            restaurant = self.restaurants.get_restaurant_by_name(name)
            ManageRestaurantMenu("manage restaurant", restaurant).run()
        except exceptions.BackMenu:
            return
        
    def run(self) -> None:
        try:
            while True:
                self.show()
                choice = self.get_choice()
                self.options[choice][1]()
        except exceptions.BackMenu:
            self.do_exit()

    def do_exit(self):
        is_confirmed = ConfirmationMenu("are you sure you want to exit?").run()
        if is_confirmed:
            self.exit()
        else:
            print("exit aborted")

    def exit(self):
        print("exiting...")
        sys.exit(0)

class ManageRestListMenu(Menu):
    def __init__(self, title: str, restaurants:Restaurants) -> None:
        super().__init__(title)
        self.restaurants = restaurants
        self.io = AppIO()
        self.add_option("c", "create a new restaurant", self.create_restaurant)
        self.add_option("p", "show all reastaurants list", self.print_restaurant_list)
        self.add_option("d", "delete an existing restaurant", self.to_delete_restaurant)
        self.add_back_key()
    
    def create_restaurant(self):
        while True:
            try:
                restaurant_name = self.io.get_name("enter your restaurant name")
                self.restaurants.add_restaurant(restaurant_name)
                print(f"{restaurant_name} successfully created")
                break
            except exceptions.RestaurantAlreadyExistsError:
                print("there is already a restaurant by this name try again")

    def print_restaurant_list(self) -> None:
        print(str(self.restaurants))

    def to_delete_restaurant(self)->None:
        name = self.io.get_name("enter the restaurant name")
        is_confirmed = ConfirmationMenu(f"are you sure you want to delete {name}? ").run()
        if is_confirmed is True:
            try:
                self.restaurants.delete_restaurant_by_name(name)
            except exceptions.RestaurantNotExistError:
                print("restaurant does no exist")    
        else:
            print("deletion aborted")

class ManageRestaurantMenu(Menu):
    def __init__(self, title: str, restaurant:Restaurant) -> None:
        super().__init__(title)
        self.restaurant = restaurant
        self.add_option("fm", "manage food menu", lambda : ManageFoodMenu("manage food menu", self.restaurant.menu).run())
        self.add_option("t", "manage tables", lambda : ManageTables("tables management", self.restaurant.tables).run())
        self.add_option("r", "manage reservations", lambda : ManageReservations("reservation management menu", self.restaurant).run())
        self.add_back_key()

class ManageFoodMenu(Menu):
    def __init__(self, title: str, menu:food_menu.Menu) -> None:
        super().__init__(title)
        self.food_menu = menu
        self.add_option("a","add dish", lambda : AddDishes("add dish", self.food_menu).run())
        self.add_option("r","remove dish", lambda : RemoveDishes("remove dish", self.food_menu).run())
        self.add_option("v", "view dishes", lambda : ViewDishes("view dishes", self.food_menu).run())
        self.add_back_key()

class AddDishes(Menu):
    def __init__(self, title: str, menu:food_menu.Menu) -> None:
        super().__init__(title)
        self.food_menu = menu
        self.io = AppIO()
        self.add_option("a", "add a first course", lambda : self.redirect_add_dish("first_course"))
        self.add_option("b", "add a main course", lambda : self.redirect_add_dish("main_course"))
        self.add_option("c", "add an additional course", lambda : self.redirect_add_dish("additional"))
        self.add_option("d", "add a drink", lambda : self.redirect_add_dish("drink"))
        self.add_option("e", "add bread", lambda : self.redirect_add_dish("bread"))
        self.add_option("f", "add a desert", lambda : self.redirect_add_dish("desert"))
        self.add_back_key()
    
    def get_dish_details(self)->DishDetails:
        name = self.io.get_name("enter dish name")
        price = self.io.get_float_input(
            "enter the dish's price",
            "price cannot be lower than 0",
            "price must be in numbers"
        )
        description = self.io.get_input("enter a dish description")
        return DishDetails(name, price, description)
    
    def redirect_add_dish(self, component_name:str):
        dish_details:DishDetails = self.get_dish_details()
        if component_name == "bread":
            quantity = self.io.get_int_input(
                "enter quantity",
                "quantity cannot be less than 1",
                "quantity must be a number",
                1
            )
            self.food_menu.add_dish(dish_details, component_name, quantity)
        else:    
            self.food_menu.add_dish(dish_details, component_name)

class RemoveDishes(Menu):
    def __init__(self, title: str, menu:food_menu.Menu) -> None:
        super().__init__(title)
        self.food_menu = menu
        self.io = AppIO()
        self.add_option("a", "remove a first course", lambda : self.redirect_remove_dish("first_course"))
        self.add_option("b", "remove a main course", lambda : self.redirect_remove_dish("main_course"))
        self.add_option("c", "remove an additional course", lambda : self.redirect_remove_dish("additional"))
        self.add_option("d", "remove a drink", lambda : self.redirect_remove_dish("drink"))
        self.add_option("e", "remove bread", lambda : self.redirect_remove_dish("bread"))
        self.add_option("f", "remove a desert", lambda : self.redirect_remove_dish("desert"))
        self.add_back_key()
        

    def redirect_remove_dish(self, component_name:str):
        while True:
            name = self.io.get_name("enter the dish's name")
            is_confirmed = ConfirmationMenu(f"are you sure you want to delete the dish {name}, from {component_name}s?\n").run()
            if is_confirmed:
                try:
                    self.food_menu.remove_dish(name, component_name)
                    print("dish successfully removed")
                    break
                except exceptions.DishNotExistError:
                    print("the dish name does not exist, try again")
            else:
                print("dish removal aborted")
                
class ViewDishes(Menu):
    def __init__(self, title: str, menu:food_menu.Menu) -> None:
        super().__init__(title)
        self.food_menu = menu
        self.io = AppIO()
        self.add_option("a", "view the first courses", lambda : self.redirect_view_dish("first_course"))
        self.add_option("b", "view the main courses", lambda : self.redirect_view_dish("main_course"))
        self.add_option("c", "view the additional courses", lambda : self.redirect_view_dish("additional"))
        self.add_option("d", "view the drinks", lambda : self.redirect_view_dish("drink"))
        self.add_option("e", "view the breads", lambda : self.redirect_view_dish("bread"))
        self.add_option("f", "view the deserts", lambda : self.redirect_view_dish("desert"))
        self.add_back_key()

    def redirect_view_dish(self, component_name:str):
        print(f"{component_name} menu:")
        print (self.food_menu.view_dishes(component_name))

class ManageTables(Menu):
    def __init__(self, title: str, tables:Tables) -> None:
        super().__init__(title)
        self.tables = tables
        self.io = AppIO()
        self.add_option("a", "add table", self.add_table)
        self.add_option("r", "remove table", self.remove_table)
        self.add_back_key()
    
    def add_table(self):
        while True:
            try:
                table_num = self.io.get_int_input(
                    "enter the table number",
                    "table number cannot be less than 0",
                    "table number must be a number, try again"
                    )
                sits = self.io.get_int_input(
                    "enter the number of sits",
                    "number of sits cannot be less than 0",
                    "number of sits must be a number, try again"
                )
                self.tables.add_table(table_num, sits)
                break
            except exceptions.TableNumberAlreadyExistError:
                print("table number already exists, try again")

    def remove_table(self):
        while True:
            table_num = self.io.get_int_input(
                "enter the table number",
                "table number cannot be less than 0",
                "table number must be a number, try again"
                )
            is_confirmed = ConfirmationMenu(f"are you sure you want to delete table number {table_num}?").run()
            if is_confirmed is True:
                try:
                    self.tables.remove_table_by_number(table_num)
                    break
                except exceptions.TableNotExistError:
                    print("there is no table by this number, try again")
            else:
                print("table deletion aborted")
                break

class ManageReservations(Menu):
    def __init__(self, title: str, restaurant:Restaurant) -> None:
        super().__init__(title)
        self.restaurant = restaurant
        self.io = AppIO()
        self.add_option("c", "create new reservation", self.create_reservation)
        self.add_option("d", "delete reservation", self.to_cancel_reservation)
        self.add_option("p", "show reservations by category", lambda : ViewReservations("sort reservations by", self.restaurant.reservations).run())
        self.add_option("m", "manage an existing reservation", lambda : self.redirect_to_manage_existing_reservation())
        self.add_back_key()

    def get_reservation_details(self) -> ReservationDetails:
        name = self.io.get_name("please enter your name")
        sits = self.io.get_int_input(
            "enter the number of sits",
            "number of sits cannot be less than 0",
            "number of sits must be a number"
        )
        start = self.io.get_reservation_start()
        duration = self.io.get_reservation_duration(self.restaurant.min_meal_time)
        return ReservationDetails(name, sits, start, duration)

    def create_reservation(self):
        print("welcome to reservation creation wizard")
        reserv_details = self.get_reservation_details()
        try:
            reservation:Reservation = self.restaurant.reservations.new_reservation(reserv_details)
            print("reservation successfully created, details.\n")
            print(str(reservation))
        except exceptions.NoAvailableTablesError:
            print("we are sorry but it seems we have no available tables at the moment try again later\n")
            self.go_back()

    def to_cancel_reservation(self):
        while True:
                reservation_id = self.io.get_int_input(
                    "enter your reservation id",
                    "reservation id cannot be less than 0", 
                    "reservation id must be a number"
                    )
                is_confirmed = ConfirmationMenu(f"are you sure you want to delete oreder {reservation_id}?").run()
                if is_confirmed is True:
                    try:
                        self.restaurant.reservations.cancel_reservation(reservation_id)
                        return
                    except exceptions.ReservationNotFoundError:
                        print("we couldn't find a reservation by this id, try again")
                else:
                    print("deletion aborted")

    def redirect_to_manage_existing_reservation(self):
        while True:
            try:
                reservation_id = self.io.get_int_input(
                    "enter the reservation id",
                    "reservation id cannot be 0 or less",
                    "reservation id must be a number"
                )
                reservation = self.restaurant.reservations.get_reservation_by_id(reservation_id)
                break
            except exceptions.ReservationNotFoundError:
                print("reservation id does not exist, try again")
        ManageExistingReservation("add dishes to reservation", reservation, self.restaurant.reservations.menu).run()

class ManageExistingReservation(Menu):
    def __init__(self, title: str, reservation:Reservation, menu:food_menu.Menu) -> None:
        super().__init__(title)
        self.reservation = reservation
        self.food_menu = menu
        self.io = AppIO()
        self.add_option("a", "order a first course", lambda : self.order_else("first_course"))
        self.add_option("b", "order a main course", lambda : self.order_else("main_course"))
        self.add_option("c", "order an additional course", lambda : self.order_else("additional"))
        self.add_option("d", "order a drink", lambda : self.order_else("drink"))
        self.add_option("f", "order a desert", lambda : self.order_else("desert"))
        self.add_option("s", "add special comments", self.add_special_comments)
        self.add_option("v", "view all dishes", lambda : ViewDishes("view dishes", self.food_menu).run())
        self.add_option("bill", "get the bill", self.get_bill)
        #bread comes with 1st course only do not change
        self.add_back_key()
        
    def order_else(self, component_name):
        spec_cases = {"desert" : self.set_up_desert, "drink" : self.set_up_drink}
        while True:
            try:
                name = self.io.get_name("enter the dish's name")
                dish:Dish = self.food_menu.get_dish_by_name(component_name, name) #type: ignore
                special_case = spec_cases.get(component_name)
                if special_case:
                    dish = special_case(dish)
                self.reservation.add_order(dish)
                print(f"{name} added to reservation")
                if component_name == "first_course":
                    bread = self.io.get_bool_input("will you like to add bread to this course? ")
                    if bread:
                        self.order_bread()
                break
            except exceptions.DishNotExistError:
                print("there is no dish by that name, try again")

    def set_up_desert(self, desert):
        sugar = self.io.get_bool_input("with sugar?")
        return ClientDesert(desert, sugar)
    def set_up_drink(self, drink):
        cold = self.io.get_bool_input("will you like the drink cold?")
        drink_size = self.io.get_validated_input(
            "enter the drink size (s/m/l)",
            lambda s: s in SIZE_MAP,
            lambda s : DrinkSizes(s)
            )
        return(ClientDrink(drink, cold, drink_size))#type: ignore

    def order_bread(self):
        while True:
            try:
                name = self.io.get_name("enter the bread's name")
                bread_inv:BreadInventory = self.food_menu.bread.get_bread_by_name(name) 
                bread:Bread = self.food_menu.bread.order_bread(bread_inv)
                self.reservation.add_order(bread)
                print(f"{name} added to reservation")
                break
            except exceptions.DishNotExistError:
                print("there is no bread by that name, try again")

    def add_special_comments(self):
        comment = self.io.get_input("enter your comment here.")
        self.reservation.add_comment(comment)

    def get_bill(self):
        meal = self.reservation.get_meal_list()
        if not meal:
            print("this reservation didn't order anything yet")
            return
        billing = Bill(meal)
        overall_bill:BillDetails = billing.overall()
        self.print_bill(overall_bill)
    
    def print_bill(self, overall_bill:BillDetails):
        print(f"price.       {overall_bill.price:.2f}$\n"\
              f"tip.         {overall_bill.tip:.2f}$\n"\
              f"tax.         {overall_bill.tax:.2f}$\n"\
              f"total price: {overall_bill.overall:.2f}$")

class ViewReservations(Menu):
    def __init__(self, title: str, reservations:Reservations) -> None:
        super().__init__(title)
        self.reservations = reservations
        self.io = AppIO()
        self.add_option("a","view all reservations",self.view_all_reservations)
        self.add_option("id","view reservation by id",self.view_reservation_by_id)
        self.add_option("st","sort reservations by start time",self.view_reservations_by_start)
        self.add_option("n","sort reservations by name",self.view_reservations_by_name)
        self.add_option("t","sort reservations by table",self.view_reservations_by_table)
        self.add_back_key()
    
    def view_all_reservations(self):
        print("all reservations list")
        for row_num, reservation in enumerate(self.reservations.get_all_reservations(), start = 1):
            print(f"{row_num}. {str(reservation)}\n")
    def view_reservation_by_id(self):
        try:
            reserv_id = self.io.get_int_input(
                "enter reservation id",
                "id cannot be less than 0",
                "id must be a number"
            )
            reservation = self.reservations.get_reservation_by_id(reserv_id)
            print(f"{str(reservation)}\n")
        except exceptions.ReservationNotFoundError:
            print("no such reservation id, try again")
            
    def view_reservations_by_name(self):
        name = self.io.get_name("enter the name")
        reservations = self.reservations.get_reservations_by_name(name)
        if len(reservations) == 0:
            print(f"there are no reservations by the name {name}")
        else:
            print(f"reservations with name {name}")
            for row_num, reservation in enumerate(reservations, start = 1):
                print(f"{row_num}. {str(reservation)}\n")   
            
    def view_reservations_by_start(self):
        raw_start = self.io.get_reservation_start()
        start = raw_start.strftime("%Y-%m-%d %H:%M")
        reservations = self.reservations.get_reservations_by_start(raw_start)
        if len(reservations) == 0:
            print(f"there are no reservations with start time {start}")
        else:
            print(f"reservations with start time {start}")
            for row_num, reservation in enumerate(reservations, start = 1):
                print(f"{row_num}. {str(reservation)}\n")

    def view_reservations_by_table(self):
        table_num = self.io.get_int_input(
            "enter the table number",
            "table number must be higher than 0",
            "able number must be a number"
        )
        reservations = self.reservations.get_reservations_by_table(table_num)
        if len(reservations) == 0:
            print(f"there are no reservations for table number {table_num}")
        else:
            print(f"reservations for table number {table_num}")
            for row_num, reservation in enumerate(reservations, start = 1):
                print(f"{row_num}. {str(reservation)}\n")

class ConfirmationMenu():
    def __init__(self, title: str) -> None:
        self.title = title
        self.options = {"y":"yes, continue", "n" : "no, go back"}
        self.io = AppIO()

    def show(self):
        print(f"\n=== {self.title} ===")
        print("y.  yes, continue \nn.  no, go back")
    
    def run(self):
        self.show()
        choice = self.io.get_choice([k for k in self.options])
        return True if choice == "y" else False
        
if __name__ == "__main__":
    pass