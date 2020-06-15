# Тестируем связь Customer c User
from Doudb.Model import CameraBrand, CameraModel,  Customer, User, Site, Camera
from typing import List
import ipaddress
from Doudb.Repo import Repo


def PrintAll(list: List):
    for item in list:
        print(f'{item = }')


def print_message(message: str, blank: bool = True):
    if blank:
        print('*'*20 +f' {message} '+ '*'*20)
    else:
        print('*' * 20 + f'{message}' + '*' * 20)


def AddCustomerUser(customer: Customer, login: str, tlg: str = "") -> User:
    print_message('Добавить пользователя')
    user: User = customer.AddUser(login)
    if tlg != "":
        user.telegram = tlg
    ok = repo.SessionCommit()
    if not ok:
        user = None
    print(f'результат добавления = {ok}')
    print(user)
    return user


def DelCustomerUser(customer: Customer, login: str):
    print_message('Удалить пользователя')
    customer.RemoveUser('bea@hotbox.ru')
    ok: bool = repo.SessionCommit()
    print(f'результат удаления = {ok}')


def SetUserTelegram(user: User, tlg_id: str, msg=''):
    print_message(msg)
    user.telegram = tlg_id
    ok = repo.SessionCommit()
    print(user)
    print(f'изменили Telegram = {ok}')


def CreateCustomerEx(cust_name: str):
    print_message(f'Добавить заказчика {cust_name}')
    customer: Customer = repo.AddCustomer(cust_name)
    print(customer)


def DelCustomerEx(cust_name: str):
    print_message(f'Удалить заказчика {cust_name}')
    ok: bool = repo.DelCustomer(cust_name)
    print(f'Результат удаления = {ok}')


# подключение к БД
repo = Repo()
session = repo.session

customers: List[Customer] = repo.GetAllCustomers()
if len(customers) == 0:
    CreateCustomerEx('Profiteam')
    CreateCustomerEx('ООО Рога и копыта')
    CreateCustomerEx('Pupkin')
    customers = repo.GetAllCustomers();

print_message('Список всех заказчиков')
PrintAll(customers)

print_message('Выбрать заказчика')
customer = repo.GetCustomer('Profiteam')
if customer is None:
    CreateCustomerEx('Profiteam')
print(customer)

user: User = None
ok: bool = False

user = AddCustomerUser(customer, 'bea@hotbox.ru', tlg='sdsdsdsdsdsd')
if user is None:
    print_message('Выбрать пользователя')
    user = customer.GetUser('bea@hotbox.ru')
    print(user)

SetUserTelegram(user, 'bea_tlg', 'добавить телеграм ид')
SetUserTelegram(user, 'new_bea_tlg', 'изменить телеграм ид')
SetUserTelegram(user, None, 'удалить телеграм ид')

DelCustomerUser(customer, 'bea@hotbox.ru')

DelCustomerEx('ООО Рога и копыта')
DelCustomerEx('Pupkin')
DelCustomerEx('Profiteam')


session.close()
