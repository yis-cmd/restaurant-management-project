from datetime import datetime, timedelta
import exceptions
class AppIO:
    def get_input(self, msg) -> str:
        while True:
            user_input = input(f"{msg}\n > ").strip().casefold()
            if user_input == "/q":
                raise exceptions.BackMenu
            if user_input:
                break
            print("empty input, try again")
        return user_input
    
    def get_validated_input(self, msg, validator, mapper = None):
        while True:
            user_input = self.get_input(msg)
            if validator(user_input):
                return mapper(user_input) if mapper else user_input
            print("invalid key! try again")
    
    def get_name(self, msg) -> str:
        while True:
            name =  self.get_input(msg)
            if not name.isdigit():
                return name
            print("name cannot be digits only")
    
    def get_reservation_start(self) -> datetime:
        while True:
            try:
                raw_date = self.get_input("enter a date and time(yyyy mm dd hh mm) \n >")
                date_parts = raw_date.split()
                year, month, day, hour, minute = map(int, date_parts)
                return datetime(year = year, month = month, day = day, hour = hour, minute = minute)
            except ValueError:
                print("datetime format has to be YYYY MM DD HH MM try again")

    def get_reservation_duration(self, min_meal_time:timedelta) -> timedelta:
        while True:
            try:
                raw_duration = self.get_input("what will be the meal's duration (minutes) \n >")
                duration = timedelta(minutes = int(raw_duration))
                if duration < min_meal_time:
                    print(f"duration cannot be less than {min_meal_time} minutes long")
                    continue
                break
            except ValueError:
                print("duration format has to be MM try again")
        return duration
    
    def get_int_input(self, msg:str, out_of_range_msg:str, not_number_msg:str, min_value:int = 0) -> int:
        while True:
            try:
                int_input = int(self.get_input(msg))
                if int_input <= min_value:
                    print(out_of_range_msg)
                    continue
                break
            except ValueError:
                print(not_number_msg)
        return int_input
    
    def get_float_input(self, msg:str, out_of_range_msg:str, not_number_msg:str, min_value:float = 0)->float:
        while True:
            try:
                int_input = float(self.get_input(msg))
                if int_input <= min_value:
                    print(out_of_range_msg)
                    continue
                break
            except ValueError:
                print(not_number_msg)
        return int_input
    
    def get_choice(self, options:list) -> str:
        choice = input("> ").strip().casefold()
        while choice not in options:
            print("invalid key, try again")
            choice = input("> ").strip().casefold()
        return choice
    
    def get_bool_input(self, msg) -> bool:
        options = {"y" : True, "yes": True, "n" : False, "no" : False}
        while True:
            value = self.get_input(f"{msg} (y/n) \n >")
            bool_value =  options.get(value) 
            if bool_value is not None:
                return bool_value
            print("invalid key! try again")