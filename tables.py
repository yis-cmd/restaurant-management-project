import exceptions
class Table:
    def __init__(self, number:int, sits:int) -> None:
        self.number = number
        self.sits = sits
        
    def __str__(self) -> str:
        return f"table number {self.number}, {self.sits} sits\n"

class Tables:
    def __init__(self) -> None:
        self.collection:list[Table] = []

    def add_table(self, number:int, sits:int):
        if number not in [table.number for table in self.collection]:
            self.collection.append(Table(number, sits))
        else:
            raise exceptions.TableNumberAlreadyExistError
    
    def remove_table_by_number(self, table_num):
            table = self.get_table_by_number(table_num)
            self.collection.remove(table)

    def __str__(self) -> str:
        return "".join([str(table) for table in self.collection])
    
    def get_table_by_sits(self, sits:int) -> list[Table]:
        return [t for t in self.collection if t.sits >= sits]
    
    def get_table_by_number(self,table_num) -> Table:
        try:
            return next(t for t in self.collection if t.number == table_num)
        except StopIteration:
            raise exceptions.TableNotExistError