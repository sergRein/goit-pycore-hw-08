from address_book import AddressBook
import pickle


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            data = pickle.load(f)
            if isinstance(data, AddressBook): #if saved data from our class
                print("Data loaded successfully")
                return data
            else:
                print("Data in file not from AddressBook, creating empty address book")
                return AddressBook()
    except FileNotFoundError:
        print("File for data load not found, creating empty address book")
        return AddressBook()
    except Exception: #some other unexpected error
        print("Some error with data load, creating empty address book")
        return AddressBook()