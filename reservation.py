from datetime import datetime, timedelta
import tables
import food_menu
import exceptions
from pydantic.dataclasses import dataclass
from courses import Dish

@dataclass
class ReservationDetails:
    name:str
    sits:int
    start:datetime
    duration:timedelta

class Reservation:
    def __init__(
                self, 
                id:int,
                name:str,
                table_num:int, 
                start:datetime, 
                duration:timedelta,
                ) -> None:
        self.id:int = id
        self.name = name
        self.table_num:int = table_num
        self.meal:list = []
        self.comments:list[str] = []
        self.start:datetime = start
        self.duration:timedelta = duration
    @property
    def end(self) -> datetime:
        return self.start + self.duration
    
    def add_order(self, dish:Dish):
        self.meal.append(dish)

    def add_comment(self, comment:str):
        self.comments.append(comment)

    def get_meal_list(self):
        return self.meal

    def __str__(self) -> str:
        meal = "\n".join([dish.name for dish in self.meal]) or "no dishes"
        start = self.start.strftime("%Y-%m-%d %H:%M")
        end = self.end.strftime("%H:%M")
        no_special_comments = "no special comments"
        special_comments = "special comments: "
        comments = "\n".join(self.comments)
        return f"reservation id. {self.id}\n"\
            f"name. {self.name}\n"\
            f"table number {self.table_num}\n"\
            f"from {start} to {end}\n"\
            f"ordered: {meal}\n" \
            f"{no_special_comments if len(self.comments) == 0 else special_comments}.\n"\
            f"{comments if len(self.comments) > 0 else ''}"

class Reservations:
    def __init__(self, tables:tables.Tables, menu:food_menu.Menu) -> None:
        self._id_count = 1
        self.tables = tables
        self.menu = menu
        self.collection:list[Reservation] = []

    def _next_id(self) -> int:
        _id = self._id_count
        self._id_count += 1
        return _id

    def _create_reservation(self, name:str, table_num:int, start:datetime, duration:timedelta) -> Reservation:
        return Reservation(id = self._next_id(),name = name, table_num = table_num, start = start, duration = duration)
    
    def _add_reservation(self, entry) -> None:
        self.collection.append(entry)

    def get_all_reservations(self) -> list[Reservation]:
        return self.collection
    def get_reservations_by_table(self, table_num:int) -> list[Reservation]:
        return [r for r in self.collection if r.table_num == table_num]
    def get_reservations_by_start(self, start:datetime) -> list[Reservation]:
        return [r for r in self.collection if r.start == start]
    def get_reservations_by_name(self, name:str) -> list[Reservation]:
        return [r for r in self.collection if r.name == name]
    def get_reservation_by_id(self, id:int) -> Reservation:
        try:
            return next(r for r in self.collection if r.id == id)
        except StopIteration:
            raise exceptions.ReservationNotFoundError
    
    def _check_overlaps(self, reservation:Reservation, start:datetime, end:datetime):
        return reservation.start < end and start < reservation.end
        
    def _check_availability_by_date(self, reservations:list[Reservation], start, end) -> bool:
        for reservation in reservations:
            overlaps = self._check_overlaps(reservation, start, end)
            if overlaps:
                return False
        return True
    
    def get_available_table(self, sits:int, start:datetime, end:datetime) -> tables.Table:
        suitable_tables:list[tables.Table] = self.tables.get_table_by_sits(sits)
        for table in suitable_tables:
            active_reservations = self.get_reservations_by_table(table.number)
            is_available = self._check_availability_by_date(active_reservations, start, end)
            if is_available is True:
                return table
        raise exceptions.NoAvailableTablesError

    def new_reservation(self,reserv_details:ReservationDetails) -> Reservation:
        """
        looks for available tables at the time specified 
        and creates a reservation for it

        Args:
            name (str): reservation creator name
            sits (int): number of sits required
            start (datetime.datetime): time to start the meal
            duration (datetime.timedelta): how much time will the meal take

        Returns:
            Reservation: the reservation object
        """
        end = reserv_details.start + reserv_details.duration
        
        table = self.get_available_table(reserv_details.sits, reserv_details.start, end)
        reservation = self._create_reservation(reserv_details.name, table.number, reserv_details.start, reserv_details.duration)
        self._add_reservation(reservation)
        return reservation
    
    def cancel_reservation(self, reservation_id:int) -> None:
        reservation = self.get_reservation_by_id(reservation_id)
        self.collection.remove(reservation)
        return None
    
    def order_dish(self, reservation_id:int, dish_name:str, section:str)->None:
        reservation = self.get_reservation_by_id(reservation_id)
        dish = self.menu.get_dish_by_name(section, dish_name)
        reservation.meal.append(dish)

if __name__ == "__main__":
    pass