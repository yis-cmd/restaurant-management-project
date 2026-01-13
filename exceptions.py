class CustomExceptions(Exception):
    pass

class TableNotExistError(CustomExceptions):
    pass

class ReservationNotFoundError(CustomExceptions):
    pass

class SectionNotExistError(CustomExceptions):
    pass

class DishNotExistError(CustomExceptions):
    pass

class TableNumberAlreadyExistError(CustomExceptions):
    pass

class NotEnoughBreadError(CustomExceptions):
    pass

class RestaurantNotExistError(CustomExceptions):
    pass

class NoAvailableTablesError(CustomExceptions):
    pass

class RestaurantAlreadyExistsError(CustomExceptions):
    pass

class BackMenu(Exception):
    pass
