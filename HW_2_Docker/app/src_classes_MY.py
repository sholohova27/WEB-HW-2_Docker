from collections import UserDict, defaultdict
from datetime import datetime, timedelta


# родительский
class Field:
    def __init__(self, value):
        if not isinstance(value, str):
            raise ValueError("Value must be string")
        else:
            self.value = value

    # теперь при вызове экземпляра объекта будет выводиться его имя, а не ячейка памяти
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)

    # obj.value -> AttributeError, хотя так писать правильнее
    def __eq__(self, obj):
        if not isinstance(obj, Field):
            return False
        return self.value == obj.value

    def __hash__(self):
        return hash(self.value)


# поле с именем
class Name(Field):
    pass


# поле с телефоном (отказалась от наследования, т.к. были ошибки
class Phone(Field):
    def __init__(self, phone = None):
# явное наследование методов, это value класса Field, по сути
        super().__init__(phone)
        self.__phone = None
        self.phone = phone

    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, value):
        if len(value) <= 5:
            raise ValueError('Phone number must have more then 5 digits')
        self.__phone = value


class Birthday(Field):
    def __init__(self, bday= None):
        super().__init__(bday)
# скрытое поле None нужно для того, чтобы при инициализации не присваивалось значение, исключенное в сеттере
# инициализация происходит до сеттера, а на вторую запись уже влияет сеттер
        self.__bday = None
        self.bday = bday

# геттер для поля bday, в этоу ветку он пойдет, если будут соблюдены условия в сеттере
    @property
    def bday(self):
        return f'{self.__bday}'

# сеттер для поля bday !!! Вводится новое для класса поле value
    @bday.setter
    def bday(self, value):
        try:
            datetime.strptime(value, '%d %B %Y')
            self.__bday = value
        except ValueError:
            raise ValueError(f'Write birthday in format like "27 August 1987"') from None

class Email(Field):
    def __init__(self, email=None):
        # явное наследование методов
        super().__init__(email)
        self.__email = None
        self.email = email

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        if value.find("@") == -1:
            raise ValueError('Email must have special symbol @')
        self.__email = value


# добавление/удаление/редактирование
class Record:
    def __init__(self, name: Name, phones: list[Phone] = None, bday = None, emails: list[Email] = None):
        self.name = name
        self.phones = phones
        self.emails = emails
        self.bday = bday

    def add_phone(self, phone: Phone):
        self.phones.append(phone)
        return f"Contact {self.name} with {phone} phone number has been added"

    def add_email(self, email: Email):
        self.emails.append(email)
        return f"Contact {self.name} with {email} email has been added"


    def del_phone(self, phone: Phone):
        for phone in self.phones:
            self.phones.remove(phone)
            return f"Phone number {phone} has been deleted from contact {self.name}"
        return f'{phone} not in list'

    def del_email(self, email: Email):
        for email in self.emails:
            self.emails.remove(email)
            return f"Email {email} has been deleted from contact {self.name}"
        return f'{email} not in list'

    def edit_phone(self, old_phone: Phone, new_phone: Phone):
        if old_phone in self.phones:
            self.del_phone(old_phone)
            self.add_phone(new_phone)
            return f"Phone number {old_phone} has been substituted with {new_phone} for contact {self.name}"
        return f'{old_phone} not in list'

    def edit_email(self, old_email: Email, new_email: Email):
        if old_email in self.emails:
            self.del_email(old_email)
            self.add_email(new_email)
            return f"Email {old_email} has been substituted with {new_email} for contact {self.name}"
        return f'{old_email} not in list'

    def days_to_birthday(self):
        if not self.bday:
            return "Birthdate not set."
        bday = datetime.strptime(self.bday.value, '%d %B %Y')
        now = datetime.now()
        bday_day = bday.day
        bday_month = bday.month
        bday_year = bday.year
        bday_cur_Y = datetime(year = now.year, month = bday_month, day = bday.day)
        diff = bday_cur_Y - now + timedelta(days = 1)
        if (bday_cur_Y - now).days >= 0:
            diff = bday_cur_Y - now + timedelta(days = 1)
        if (bday_cur_Y - now).days < 0:
            bday_next_Y = datetime(year = now.year + 1, month = bday_month, day = bday.day)
            diff = bday_next_Y - now + timedelta(days = 1)
        return f'{self.name}, {self.bday}: {diff.days} days left to your birthday'


    def __str__(self):
        return f'{self.phones}'

    def __repr__(self):
        return str(self)

    # добавляем метод get для ф-ии bday_on_week_func()
    def get(self, key):
        return getattr(self, key)


# поиск по записям
class AddressBook(UserDict):
    # ожидает поля объекта Record (name, phone)
    def add_record(self, record: Record):
        # эта запись приводила к проблемам с сериализацией: if record.name == self.get('name')
        if self.get(record.name.value):
            return f'{record.name.value} is already in contacts'
        # data - поле UserDict
        # т.к. в классе Name есть маг. метод __str__, можно просто record.name
        # добавили value и-за проблем с сериализацией
        self.data[record.name.value] = record
        return f'{record.name.value} with {record.phones} phone and birthday {record.bday}  is successfully added in contacts'

    def show_all(self):
        return self.data

    def phone(self, name):
        try:
            return self.data[name]
        except KeyError:
            return f'Contact {name} is absent'

    def paginator(self, records_num):
        start = 0
        while True:
            # превращаем в список ключи словаря и слайсим
            result_keys = list(self.data)[start: start + records_num]
            # превращаем список ключей словаря в список строк с форматом "ключ : [значение]"
            # result_list = [f"{key} : {self.data.get(key)}" for key in result_keys]
            result_list = [f"{key} : {self.data.get(key).phones}, {self.data.get(key).emails}, {self.data.get(key).bday}" for key in
                           result_keys]
            if not result_keys:
                break
            yield '\n'.join(result_list)
            start += records_num

# явно применяет str ко всем элементам словаря, в качестве ключа используется имя, которое есть и в значениях, по которым мы итерируемся (нужно это из-за ошибок при сохранении контакта в json)
    def to_dict(self):
        data = {}
        for value in self.data.values():
            data.update({str(value.name): {"name": str(value.name),
                                      "phones":[str(p) for p in value.phones],
                                      "emails": [str(p) for p in value.emails],
                                      "bday": str(value.bday)}})
            # self.data[key] = [[str(phone) for phone in self.data[key][0]],self.data[key][1]]
        return data

# извлекает из словаря записи, преобразует их в объекты классов, и добавляет объекты класса Record обратно в словарь
    def from_dict(self, data):
        for name in data:
            rec = data[name]
            self.add_record(Record(Name(rec['name']),
                                   [Phone(p) for p in rec['phones']],
                                   None if rec['bday'] == "None" else Birthday(rec['bday'])))

    def get_birthdays_in_x_days(self, x: int) -> str:
        today = datetime.today().date()
        future_date = today + timedelta(days=x)
        # пустой список в качестве значений для всех ключей словаря
        weeks_dict = defaultdict(list)

        for value in self.data.values():
            if value.get('bday'):
                # превращаем объект класса Birthday в дату
                date = datetime.strptime(value.get('bday').value, '%d %B %Y')
                # превращаем в дату текущего года
                bday = datetime.strptime(f"{date.strftime(('%d %B'))} {datetime.now().year}", '%d %B %Y').date()
                days_left = (bday-future_date).days
                if days_left == 0:
                    weeks_dict[f'In {x} days from today'].append(value.name.value)
                elif days_left == 1:
                    weeks_dict[f'Next day after {x} days from today'].append(value.name.value)
                elif 1 < days_left <= 7:
                    weeks_dict[bday.strftime('%A, %d %B')].append(value.name.value)


        output_str = ''
        if weeks_dict:
            for day, contacts in weeks_dict.items():
                contacts_str = ', '.join(contacts)
                output_str += f'{day}: {contacts_str}\n'
            return output_str
        return f'There are no birthdays in {x} days from today + 7 days after'


    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        results = []
        for name, record in self.items():
            result = f"{name} : {record}"
            results.append(result)
        return '\n'.join(results)

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, item):
        self.data[key] = item