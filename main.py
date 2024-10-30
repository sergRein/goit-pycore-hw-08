from address_book import AddressBook, show_menu, add_contact, change_contact, show_phone, add_birthday, show_birthday, upcoming_birthdays
from save_data import load_data, save_data

def parse_input(user_input: str) -> tuple[str, list[str]]:
    parts = user_input.split() #split all input args
    cmd = parts[0].strip().lower() if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    return cmd, args

commands = { #separate all commands
    "hello": lambda args, book: "How can I help you?",
    "add": add_contact,
    "change": change_contact,
    "phone": show_phone,
    "all": lambda args, book: str(book),
    "add-birthday": add_birthday,
    "show-birthday": show_birthday,
    "birthdays": upcoming_birthdays,
}

def main(book) -> None:
    print("Welcome to the assistant bot!")
    print(show_menu()) #show available options
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command in ["help", "menu"]:
            print(show_menu())

        elif command in commands:
            result = commands[command](args, book)
            print(result)

        else:
            print("Invalid command.")


if __name__ == '__main__':
    book = load_data()
    main(book)
    save_data(book)