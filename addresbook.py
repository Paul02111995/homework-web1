from abc import ABC, abstractmethod
from collections import UserDict
from datetime import datetime, timedelta

class UserView(ABC):
    @abstractmethod
    def display(self, message):
        pass

class ConsoleView(UserView):
    def display(self, message):
        print(message)

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be 10 digits")

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, number):
        self.phones.append(Phone(number))

    def remove_phone(self, number):
        updated_phones = []
        for phone in self.phones:
            if phone.value != number:
                updated_phones.append(phone)
        self.phones = updated_phones

    def edit_phone(self, old_number, new_number):
        if not any(phone.value == old_number for phone in self.phones):
            raise ValueError("Old phone number is not exist")    
        
        if len(new_number) != 10 or not new_number.isdigit():
            raise ValueError("New phone number must be 10 digits")
        
        for phone in self.phones:
            if phone.value == old_number:
                phone.value = new_number
                break

    def find_phone(self, number):
        for phone in self.phones:
            if phone.value == number:
                return phone
        return None
    
    def add_birthday(self, value):
        if self.birthday is None:
            self.birthday = Birthday(value)
        else:
            raise ValueError("Only one birthday is allowed per record.")

    def __str__(self):
        phones = "; ".join([phone.value for phone in self.phones])
        birthday_str = f", Birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error: {str(e)}"
    return wrapper

def parse_input(user_input):
    return user_input.split()

@input_error
def add_contact(args, book: AddressBook, view: UserView):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    view.display(message)

@input_error
def add_birthday(args, book, view):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        view.display(f"Birthday added for {name}.")
    else:
        view.display(f"Contact {name} not found.")

@input_error
def show_birthday(args, book, view):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        view.display(f"{name}'s birthday is on {record.birthday}.")
    else:
        view.display(f"Contact {name} not found or birthday not set.")

@input_error
def birthdays(args, book, view):
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    birthday_list = []
    for record in book.data.values():
        if record.birthday:
            birthday = record.birthday.value
            birthday_this_year = birthday.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=birthday_this_year.year + 1)
            days_to_birthday = (birthday_this_year - today).days
            if 0 <= days_to_birthday <= 7:
                congratulation_date = birthday_this_year

                if congratulation_date.weekday() >= 5:
                    days_until_monday = (7 - congratulation_date.weekday()) % 7
                    congratulation_date += timedelta(days=days_until_monday)

                birthday_list.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%Y.%m.%d"),
                })

    if birthday_list:
        result = "\n".join([f"{user['name']}: {user['congratulation_date']}" for user in birthday_list])
        view.display(f"Upcoming birthdays in the next week:\n{result}")
    else:
        view.display("No birthdays in the next week.")

@input_error
def change_phone(args, book, view):
    if len(args) != 3:
        view.display("Invalid command. Please provide name, old phone number, and new phone number after 'change'.")
        return
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        try:
            if old_phone not in [phone.value for phone in record.phones]:
                view.display(f"Error: Old phone number {old_phone} not found for {name}.")
                return
            
            record.edit_phone(old_phone, new_phone)
            view.display(f"Phone number updated for {name}.")
        except ValueError as e:
            view.display(f"Error: {str(e)}")
    else:
        view.display(f"Contact {name} not found.")

@input_error
def show_phone(args, book, view):
    if len(args) != 1:
        view.display("Invalid command. Please provide a name after 'phone'.")
        return
    
    name = args[0]
    record = book.find(name)
    
    if record:
        phone_numbers = [str(phone) for phone in record.phones]
        view.display(f"{name}'s phone number is {', '.join(phone_numbers)}.")
    else:
        view.display(f"Contact {name} not found.")

@input_error
def show_all_contacts(book: AddressBook, view: UserView):
    contacts = []
    for record in book.data.values():
        contacts.append(str(record))
    view.display("\n".join(contacts) if contacts else "Address book is empty.")

def main(view: UserView):
    book = AddressBook()
    view.display("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip()
        
        if not user_input:
            view.display("Command not entered. Please enter a command.")
            continue

        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            view.display("Good bye!")
            break

        elif command == "hello":
            view.display("How can I help you?")

        elif command == "add":
            add_contact(args, book, view)

        elif command == "change":
            change_phone(args, book, view)

        elif command == "phone":
            show_phone(args, book, view)

        elif command == "all":
            show_all_contacts(book, view)

        elif command == "add-birthday":
            add_birthday(args, book, view)

        elif command == "show-birthday":
            show_birthday(args, book, view)

        elif command == "birthdays":
            birthdays(args, book, view)

        else:
            view.display("Invalid command.")

if __name__ == "__main__":
    main(ConsoleView())
