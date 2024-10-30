from collections import UserDict, defaultdict
from datetime import datetime, timedelta
from functools import wraps
import calendar

class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self,name: str):
        super().__init__(name)


class Phone(Field):
    def __init__(self, number: str):   
        super().__init__(self.__is_valid_number(number))
    
    def __is_valid_number(self, number: str):
        if len(number) != 10 or not number.isdigit():
            raise ValueError("Wrong phone number format. Must be 10 digits")  
        return number
    
    def update_number(self, new_number: str):
        self.value = self.__is_valid_number(new_number)


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None


    def __str__(self):
        to_return = f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
        if self.birthday:
            to_return += f", birthday: {self.birthday}"

        return to_return

    def show_phones(self):
        return f"{self.name} phones: {'; '.join(p.value for p in self.phones)}"

    def add_phone(self,phone: str):
        self.phones.append(Phone(phone))


    def edit_phone(self, old_phone: str, new_phone: str):
        phone = self.find_phone(old_phone)
        if phone:
            phone.update_number(new_phone)
            return
        
        raise ValueError("No such old phone")
    

    def find_phone(self, number: str):
        for phone in self.phones:
            if phone.value == number:
                return phone
            
        return None
    
    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

        
class Birthday(Field):
    def __init__(self, value: str):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format for birthdat. Use DD.MM.YYYY")
        
    def __str__(self):
        return f"{self.value.strftime('%d.%m.%Y')}"
        

class AddressBook(UserDict):
    def __init__(self):
        super().__init__()

    def __str__(self):
        to_return = "Records in book"
        for record in self.data.values():
            to_return += f"\n{record}"
        return to_return

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        if name in self.data:
            return self.data[name]
        
        return None

    def delete(self, name: str):
        if name not in self.data:
            raise KeyError(f"Record for name '{name}' not found")
        del self.data[name]

    def show_upcoming_birthdays(self, period = 'upcoming'):
        today = datetime.today().date()
        congratulation_dict = defaultdict(list)
        #generate perod for dats range
        if period == 'next-month':
            if today.month == 12:
                next_month = 1
                next_year = today.year + 1
            else:
                next_month = today.month + 1
                next_year = today.year

            date_start = datetime(next_year, next_month, 1).date()
            days_in_next_month = calendar.monthrange(next_year, next_month)[1]
            date_end = datetime(next_year, next_month, days_in_next_month).date()

        elif period == 'next-week':
            date_start = today + timedelta(days=(7 - today.weekday()))
            date_end = date_start + timedelta(days=6)
        else:
            date_start = today 
            date_end = date_start + timedelta(days=6)
    
        for username, user in self.data.items():
            if user.birthday:
                user_birthday = user.birthday.value.replace(year=today.year)
                user_birthday = user_birthday.replace(year=today.year + 1) if today > user_birthday else user_birthday
                
                if date_start <= user_birthday <= date_end:
                    day_label = f"{user_birthday.strftime('%A')} ({user_birthday.strftime('%d.%m.%Y')})"
                    congratulation_dict[day_label].append(username)


        output = ''
        for day, names in sorted(congratulation_dict.items()):
            output += f"{day}: {', '.join(names)}\n"
        
        output = "No birthdays for this period" if output == '' else output
        return output



class ChangeUserContactError(Exception):
    pass


def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError: 
            return("No such user")
        except IndexError: 
            return("Contact not found")
        except ValueError as e:
            return(f"{e}")
        except ChangeUserContactError as e:
            return(f"{e}")
    return inner


def show_menu() -> str: #print menu with available options
    MENU = """
    Commands for use:
        help or menu -- show available commands
        hello -- show hello message
        all -- show all phones in address book
        add [name] [phone] -- add new record
        change [name] [old_phone] [new_phone] -- change phone number for user with name [name]
        phone [name] -- show phone for user with name [name]
        add-birthday [name] [date] -- add birthda for user 
        show-birthday [name] -- show birthday for user
        birthdays ([period]) -- show birtdays period is optional, by default shows birthdays for next 7 days from today
                                (options for "period" param are:
                                    "next-week" to show birthdays on next week
                                    "next-month" to show birthdays for next month
                                )
        close or exit -- exit from program
    """
    return(MENU)


def get_contact_from_book(name, book: AddressBook) -> Record:
    record = book.find(name)
    if not record:
        raise KeyError
    return record

@input_error
def add_contact(args, book: AddressBook) -> str:
    if len(args) != 2:
        raise ValueError("Give me name and phone please.")
    name, phone = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook) -> str:
    if len(args) != 3:
        raise ChangeUserContactError("Wrong number of arguments provide user old phone and new phone")
    
    name, old_phone, new_phone = args
    record = get_contact_from_book(name, book)
    record.edit_phone(old_phone, new_phone)
    return "Phone changed"
        

@input_error
def show_phone(args, book: AddressBook) -> str:
    if len(args) != 1:
        raise ValueError("Please priovide user name")
    
    name = args[0]
    record = get_contact_from_book(name, book)
    return record.show_phones()

@input_error
def add_birthday(args, book: AddressBook) -> str:
    if len(args) != 2:
        raise ValueError("Please priovide user name and birthday")
    
    name, birthday = args
    record = get_contact_from_book(name, book)
    record.add_birthday(birthday)
    return "Birthday added"


@input_error
def show_birthday(args, book: AddressBook) -> str:
    if len(args) != 1:
        raise ValueError("Please priovide user name")
    
    name = args[0]
    record = get_contact_from_book(name, book)
    if not record.birthday:
        raise ValueError("Birthday for user is not set")
    return record.birthday

@input_error
def upcoming_birthdays(args, book: AddressBook) -> str:
    if len(args) == 0:
        period = 'upcoming'
    elif len(args) == 1:
        period = args[0]
        if period not in ('next-week', 'next-month'):
            raise ValueError("Available arguments for time period is 'next-week' or 'next-month'")
    else:
        raise ValueError("Provide 0 or 1 arguments for upcoming birthdays: 0 arguments for next 7 days, 1 argument for desire time period")
    
    return book.show_upcoming_birthdays(period)
