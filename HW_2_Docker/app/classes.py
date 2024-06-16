import json
import re
from collections import UserDict
from datetime import date


class Field:
    def __init__(self, value):
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f'{self.value}'


class UserName(Field):
    pass


class PhoneNumber(Field):
    def __init__(self, number):
        self.__number = None
        self.value = number

    @property
    def value(self):
        return self.__number

    @value.setter
    def value(self, val):
        # pattern = re.compile(r"(380)?(\s*)?\d{3}(\s*)?\d{3}(\s*)?\d{3}")

        new_phone = (
            val.strip()
            .removeprefix("+")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
        )

        # if not pattern.match(new_phone):
        #     raise ValueError('Invalid number')
        self.__number = new_phone


class Birthday():
    def __init__(self, day):
        self.data = None
        self.__day = day

    @property
    def day(self):
        return self.__day

    @day.setter
    def day(self, value):
        if type(value) == date:
            self.__day = value
        else:
            raise TypeError


class Record:
    def __init__(self,
                 name: UserName,
                 number: PhoneNumber,
                 birthday: Birthday = None):
        self.name = name
        self.birthday = birthday
        self.numbers = []
        if number:
            self.numbers.append(number)

    def __repr__(self) -> str:
        return f'{self.name.value.capitalize()}'

    def add_number(self, number):
        numbers = self.numbers
        number = number
        if number in numbers:
            return "This phone number is in your contacts"
        numbers.append(number)
        return f"{number} phone number is added to {self.name}'s contacts"

    def get_number(self):
        return self.numbers

    def change_number(self, old_number, new_number):
        for num in self.numbers:
            if num.value == old_number.value:
                self.numbers.remove(num)
                self.numbers.append(new_number)
                return f"Changet {old_number} to {new_number}"
        return "Number no found"

    def add_birthday(self, birthday):
        self.birthday = birthday

    def days_to_birthday(self):
        birthday = self.birthday.day
        today = date.today()

        delta1 = date(today.year, birthday.month, birthday.day)
        delta2 = date(today.year + 1, birthday.month, birthday.day)

        return ((delta1 if delta1 > today else delta2) - today).days


class ContactsBook(UserDict):

    def save_data(self, file):
        data = {}
        for value in self.data.values():
            data.update({f'{value.name}': {"name": str(value.name),
                                           "numbers": [str(ph) for ph in value.numbers],
                                           "birthday": str(value.birthday)
                                           }})
        with open(file, 'w') as fh:
            json.dump(data, fh, indent=4, ensure_ascii=False)

    def add_contact(self, contact: Record):
        self.data[contact.name.value] = contact

    def load_data(self, file):

        with open(file, "r") as fh:
            data = json.loads(fh.read())

        if data:
            for n in data:
                print(data[n])
                rec = data[n]
                name_from_data = UserName(rec['name'])
                phones = [PhoneNumber(ph) for ph in rec['numbers']]
                birthday = None if rec['birthday'] == "None" else Birthday(date.strptime(rec['birthday'], '%Y-%m-%d'))
                self.add_contact(Record(name_from_data, phones, birthday))
        else:
            pass

    def search(self, param):
        if len(param) < 3:
            return "Param < 3"
        result = []
        for rec in self.values():
            if param in str(rec):
                result.append(rec)
        return '\n'.join(result)


if __name__ == "__main__":
    name = UserName('Jon')
    phone = PhoneNumber('380974736548')
    bh = Birthday(date(1995, 4, 5))
    record = Record(name, phone, bh)

    print(record)
    print(record.days_to_birthday())