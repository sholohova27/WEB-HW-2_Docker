import json
# эта ошибка возникала при пустом файле contacts.json, ментор посоветовал импортировать ее явно
from json.decoder import JSONDecodeError
import re
from src_classes_MY import Name, Phone, Record, Birthday, AddressBook




# Загружаем словарь из файла или создаем пустой словарь (для сохранения данных)
def read_contacts(file_name):
    try:
        with open(file_name, 'r') as f:
            contacts = json.load(f)
    except (FileNotFoundError, AttributeError, JSONDecodeError):
        contacts = {}
    return contacts


# Записываем контакты в файл
def save_contacts(file_name, contacts):
    with open(file_name, 'w') as f:
        if contacts:
            json.dump(contacts, f)


def Error_func(func):
    def inner(*args, **kwargs):
        name = Name(args[0].strip().lower())
        contacts = AddressBook(kwargs['contacts'])

        try:
            return func(*args, **kwargs)
        except IndexError:
            return f'Print name and phone/s number via space', contacts
        except KeyError:
            return f'Contact {name} is absent', contacts
        except TypeError as e:
            return (f'If you try to add new contact, contact {name} is already exists.\n'
                   f'If you try to edit contact, contact {name} doesn`t exist'), contacts
        except AttributeError:
            ...
    return inner

# contacts возвращаем для того, чтобы сигнатура ф-й была одинаковая,
# kwargs['contacts']: 'contacts' это также ключ, по к-му можно найти в kwargs словарь contacts
def hello_func(*args, **kwargs):
    contacts = kwargs['contacts']
    return "How can I help you?", contacts

def help_func(*args, **kwargs):
    contacts = kwargs['contacts']
    return ''' 
               To add contacts type "add" and contact`s name after. You can also add phones (>5 digits each), birthdate (format like '27 August 1987' wo quotes), email, notes after name 
               or leave these fields empty. You can also add phone number using this command after contact was created by it`s name. 
               To change contact`s phone number type "change" and contact`s name after, old phone you want to change and new phone (>5 digits) at the end.
               To get contact`s phone numbers type "phone" and contact`s name after.
               To get contact`s birthday type "bd" and contact`s name after.
               To see all contacts with birthday in next n days from today, type "reminder n" (for example, 'reminder 0' wo quotes). You also`ll get contacts with bithday in next 7 days 
               after the date you want to check.
               To get all contacts in your notebook type "show all/show", to get n records, type "show n" wo quotes.
               To delete contact type "delete" and contact`s name after.
               To exit and save changes type "bye"/"close"/"exit"/"." 
            ''', contacts


# передаем словарь Contacts из ф-и main в качестве аргумента
@Error_func
def add_func(*args, **kwargs):
    # делаем наши переменные объектами соответствующих классов
    # и переносим их с блока try в начало ф-и
    # contacts делается экземпляром класса в мейне
    contacts = kwargs['contacts']
    name = Name(args[0].strip().lower())
    phones = []
    emails = []
    bday = None
    if args[1:]:
        for arg in args[1:]:
            if len(arg)>5:
                match_phone = re.findall(r'\b\+?\d{1,3}-?\d{1,3}-?\d{1,7}\b', str(arg))
                if match_phone:
                    phones.extend([Phone(phone.strip().lower()) for phone in match_phone])  # создаем экземпляры класса Phone из match_phone и добавляем их в список phones
            match_bd = re.search(r'\b(\d{1,2})\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{4})\b',' '.join(args[1:]), re.IGNORECASE)
            if match_bd:
                bday = Birthday(f"{match_bd.group(1)} {match_bd.group(2)} {match_bd.group(3)}")
            match_email = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', str(arg))
            if match_email:
                emails.extend(email.strip() for email in match_email)
    # создаем новые переменные rec, phones и bday, чтобы работать с классом Record
    rec = Record(name, phones, bday, emails)
    # Забираем первый и второй элемент, т.к. ф-я handler, которую вызываем в мейне,
    # возвращает ф-ю и очищенный от команды список, к-й распаковывается через * в
    # позиционные параметры add_func (в мейне): result, contacts = func(*text, Contacts=Contacts)
    # без маг. метода hash в классе тут будет ошибк, без str не работает!
    if not contacts.get(str(name)):
        contacts.add_record(rec)
        return f"Contact {name} with phone {phones} and birthday '{bday}' and email {emails} successfully added", contacts
    # вместо contacts[name] = phone присваиваем метод класса AddressBook
    contact = contacts.get(str(name))
    contact.add_phone(*phones)
    contact.add_phone(*emails)
    save_contacts(file_name, contacts.to_dict())
    return f"Phone {phones} and email {emails} added to contact {name}.", contacts



@Error_func
def change_func(*args, **kwargs):
    contacts = kwargs['contacts']
# Забираем первый и второй элемент, т.к. ф-я handler, которую вызываем в мейне,
# возвращает ф-ю и очищенный от команды список, к-й распаковывается через * в
# позиционные параметры add_funс (в мейне): result = func(*text, Contacts=Contacts)
    name = Name(args[0].strip().lower())
    #old_phone = contacts.get(name) Це буде не old_phone, а екземпляр Record
    # contacts[name] = ""
    # phones = contacts.get(str(name))[0]
    old_phone = Phone(args[1].strip().lower()) # буде на першій позиції в аргсах
    new_phone = Phone(args[2].strip().lower()) # буде на другій позиції в аргсах
    # rec = Record(name,new_phone) екземпляр Record потрібно дістати з книги контактів
    # если имени нет в словаре, оно добавится, если нет - поменяется номер
    # contacts[name] = new_phone
    # метод edit_phone у нас для списка, мы извлекаем список по ключу словаря
    rec = contacts.get(str(name))
    if rec:
        rec.edit_phone(old_phone, new_phone)
    # rec = contacts.get(str(name))
    # без str не работает, либо rec = contacts.get(name.value)
    # if rec:
    #     rec.edit_phone(old_phone, new_phone)
        return f"Phone for contact {name} changed successfully.\nOld phone {old_phone}, new phone {new_phone}", contacts
    # return f"Phone {new_phone} for contact {name} added successfully.", contacts
    save_contacts(file_name, contacts.to_dict())
    return f"Contact {name} doesn't exist", contacts




@Error_func
def del_func(*args, **kwargs):
    contacts = kwargs['contacts']
# Забираем первый и второй элемент, т.к. ф-я handler, которую вызываем в мейне,
# возвращает ф-ю и очищенный от команды список, к-й распаковывается через * в
# позиционные параметры add_funс (в мейне): result = func(*text, Contacts=Contacts)
    name = Name(args[0].strip().lower())
    # без str не находит ключ! (либо добавлять value)
    contacts.pop(str(name))
    save_contacts(file_name, contacts.to_dict())
    return f"Contact {name} successfully deleted", contacts

@Error_func
def phone_func(*args, **kwargs):
    contacts = kwargs['contacts']
    name = Name(args[0].strip().lower())
    return str(contacts.get(str(name))), contacts

# @Error_func
def bday_func(*args, **kwargs):
    contacts = kwargs['contacts']
    name = Name(args[0].strip().lower())
    # bd = str(Birthday(contacts.get(str(name))[1]))
# метод применяем к экземпляру класса
    try:
        rec = contacts.get(str(name))
        if rec:
            return rec.days_to_birthday(), contacts
    except AttributeError:
        return "You need to exit and save contacts before using bd.", contacts
    return f"Contact {name} doesn't exist", contacts


def show_func(*args, **kwargs):
    contacts = kwargs['contacts']
    if contacts:
        if len(args) > 0:
            try:
                records_num = int(args[0].strip())
                for record in contacts.paginator(records_num):
                    return record, contacts
            except ValueError:
                pass
        for record in contacts.paginator(records_num = len(contacts)):
                return record, contacts
    return "No contacts", contacts


def get_birthdays_in_x_days(*args, **kwargs):
    contacts = kwargs['contacts']
    if contacts:
        if len(args) > 0:
            try:
                x = int(args[0].strip())
                return contacts.get_birthdays_in_x_days(x), contacts
            except ValueError:
                pass
            except AttributeError:
                return "You need to exit and save contacts before using reminder.", contacts
        return "Type days number from today", contacts
    return "No contacts found", contacts


# def find_func(*args, **kwargs):
#     contacts = kwargs["contacts"]
#     n = args[0].strip().lower()
#     result = []
#     for key, value in contacts.items():
#             if n in key or \
#                     (isinstance(value, list) and any(n in phone for phone in value[1]) \
#                     or n.lower() in value[2].strip().lower()):
#                 result.append(f"{key} : {value}")
#     return '\n'.join(result) or None, contacts



def find_func(*args, **kwargs):
    contacts = kwargs["contacts"]
    n = args[0].strip().lower()
    result = []
    for key, value in contacts.items():
            if n in value.get("name").value or n.lower() in value.get("bday").value.strip().lower() \
                    or any(n in str(phone.phone) for phone in value.get("phones")):
                    # or any(n in str(email.email) for email in value.get("emails")):
                result.append(f"{key} : {value}")
    return '\n'.join(result) or f"There are no results with {n}", contacts



def unknown_command(*args, **kwargs):
    contacts = kwargs['contacts']
    return "Sorry, unknown command. Try again", contacts


def exit_func(*args, **kwargs):
    contacts = kwargs['contacts']
    return "Bye", contacts

# Ф-я handler проверяет, является ли введенный текст командой, сверяясь со словарем MODES,
# и возвращает нужную ф-ю, а также текст после команды
# никаких изменений в связи с перестройкой на классы
def handler(text):
    for command, func in MODES.items():
        if text.lower().startswith(command):
            return func, text.replace(command,'').strip().split()
    # else тут нельзя, он вернет только 1-ю ф-ю словаря MODES, если ей соответствует введенная
    # команда, но следующей ф-ции она уже соответствовать не будет, поэтому вернет unknown_command для всех остальных
    return unknown_command, []
# у ретернов должна быть одинаковая структура, поэтому после 2-го возвращаем [] (None приводит к ошибке, потому что его нельзя распаковать *),
# и обязательно добавляем 2-ю переменную в ф-и Main (func, text = handler(input('>>>'))), т.к. handler возвращает 2
# и теперь нужно добавить в каждую ф-цию параметр *args, потому что в ф-ции теперь нужно передавать этот параметр тоже


# Создаем словарь MODES из всех промежуточных ф-ций (каррирование)
MODES = {"hello": hello_func,
         "add": add_func,
         "change": change_func,
         "help": help_func,
         "delete": del_func,
         "phone": phone_func,
         "bd": bday_func,
         "reminder": get_birthdays_in_x_days,
         "show": show_func,
         "find": find_func,
         "close": exit_func,
         "exit": exit_func,
         "bye": exit_func,
         ".": exit_func}


# Передаем имя файла и путь к файлу с контактами в качестве аргументов
def main(file_name):
    # делаем словарь экземпляром объекта AddressBook, и все, contacts только тут, не нужно делать то же самое и  перезаписывать в ф-циях
    contacts = AddressBook()
    contacts.from_dict(read_contacts(file_name))
    # обязательно нужно распаковать кортеж, иначе вывод текста будет некрасивым
    result, contacts = help_func(contacts=contacts)
    print(result)
    while True:
        # Ф-я handler проверяет, является ли введенный текст командой, сверяясь со словарем MODES,
        # и возвращает нужную ф-ю, а также список из текста после команды
        func, text = handler(input('>>>'))
        # можно просто result, но так легче масштабировать, перезаписывая в contacts
        # вместо исходного словаря результат выполнения ф-ций
        if func:
            result, contacts = func(*text, contacts = contacts)
            print(result)
        if func == exit_func:
            save_contacts(file_name, contacts.to_dict())
            break



# Проверяем, что скрипт запущен как основной
if __name__ == '__main__':
    file_name = 'contacts.json'
    main(file_name)
