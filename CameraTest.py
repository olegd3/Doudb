# Тестируем работу с классом Camera
from Model import CameraBrand, CameraModel,  Customer, User, Site, Camera
from typing import List
import ipaddress
from Repo import Repo


def AddBrandModel(brand: CameraBrand, model_name: str) -> CameraModel:
    print_message('Добавить модель камеры')
    model: CameraModel = brand.AddCameraModel(model_name)
    ok: bool = repo.SessionCommit()
    if not ok:
        model = None
    print(f'результат добавления = {ok}')
    print(model)
    return model


def AddCustomer(customer_name: str) -> Customer:
    customer = Customer(customer_name)
    session.add(customer)
    ok: bool = repo.SessionCommit()
    if not ok:
        customer = None
    return customer


def AddCustomerUser(customer: Customer, login: str, tlg: str="") -> User:
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


def PrintAll(list: List):
    for item in list:
        print(f'{item=}')


def print_message(message: str, blank: bool = True):
    if blank:
        print('*'*20 +f' {message} '+ '*'*20)
    else:
        print('*' * 20 + f'{message}' + '*' * 20)


def DelSiteEx(site_name: str):
    print_message(f'Удалить место размещения видеокамер')
    ok: bool = repo.DelSite(site_name)
    print(f'Результат удаления: {ok}')


def SetIpForAllCamerasEx(model: CameraModel):
    ip_adresses: List[ipaddress.IPv4Address] = list(ipaddress.ip_network('192.168.0.0/29').hosts())
    for camera, ip in zip(model.Cameras, ip_adresses):
        ok: bool = repo.SetCameraIp(camera, ip)
        print(f'{ok}')
    print_message('Изменим ip всех камер для модели Sony')
    PrintAll(model.Cameras)


def ClearCustomerCameras(customer: Customer):
    print_message('удалить все камеры пользователя')
    for camera in customer.Cameras:
        ok: bool = repo.DelCamera(camera)
        print(f'результат удаления камеры = {ok}')


def ClearModelCameras(model: CameraModel):
    print_message(f'удалить все камеры для модели \"{model.CameraName}\"')
    for camera in model.Cameras:
        ok: bool = repo.DelCamera(camera)
        print(f'результат удаления камеры = {ok}')


def DelCustomerEx(cust_name: str):
    print_message(f'Удалить заказчика {cust_name}')
    ok: bool = repo.DelCustomer(cust_name)
    print(f'Результат удаления = {ok}')


# connect and create session
repo = Repo()
session = repo.session

brand: CameraBrand = repo.GetCameraBrand('Sony')
if brand is None:
    brand = repo.AddCameraBrand('Sony')
print_message('Выбрать брент Sony')
print(f'{brand}')


model_01: CameraModel = brand.GetCameraModel('sony_model_01')
if model_01 is None:
    model_01 = AddBrandModel(brand, 'sony_model_01')
model_02: CameraModel = repo.GetCameraModel('sony_model_02')
if model_02 is None:
    model_02 = AddBrandModel(brand, 'sony_model_02')
print_message('Все модели видеокамер Sony')
PrintAll(brand.Models)

customer: Customer = repo.GetCustomer('Profiteam')
if customer is None:
    customer = AddCustomer('Profiteam')
print_message('выбрать заказчика: Profiteam')
print(customer)

user_01: User = customer.GetUser('bea@hotbox.ru')
if user_01 is None:
    user_01 = AddCustomerUser(customer, 'bea@hotbox.ru')
print_message('выбрать пользователя: bea@hotbox.ru')
print(user_01)

user_02: User = repo.GetUser('dou@mail.ru')
if user_02 is None:
    user_02 = AddCustomerUser(customer, 'dou@mail.ru')
print_message('Выбрать пользователя dou@mail.ru')
print(user_02)

site: Site = repo.GetSite('Стройка века')
if site is None:
    site = repo.AddSite(site_name='Стройка века', address='ул. Пушкина, д. Колотущкина 15')
print_message('Выбрать объект располжения камер')
print(site)

print_message('Добавим заказчику новые камеры')
camera_01: Camera = None
camera_02: Camera = None
if len(model_01.Cameras) == 0:
    camera_01 = repo.AddCamera(customer=customer, model=model_01)
else:
    camera_01 = session.query(Camera).filter_by(CustomerId=customer.Id, ModelId=model_01.Id).first()

if len(model_02.Cameras) == 0:
    camera_02 = repo.AddCamera(customer=customer, model=model_02)
else:
    camera_02 = session.query(Camera).filter_by(CustomerId=customer.Id, ModelId=model_02.Id).first()
print(camera_01)
print(camera_02)


print_message('Все камеры выбранной модели model_02')
PrintAll(model_01.Cameras)
print_message('Все камеры заказчика')
PrintAll(customer.Cameras)

SetIpForAllCamerasEx(model_01)

print_message('Добавим характеристику Resolution для модели камеры')
model_01.AddProperty("Resolution", "1024x740")
ok: bool = repo.SessionCommit()
print_message(f'результат добавления характеристики resolution')
print_message('Все характеристики для модели model_01')
PrintAll(model_01.Properties)

model_01.RemoveProperty("Resolution")
ok = repo.SessionCommit()
print_message(f'Результат удаления характеристики Resolution = {ok}')

print_message('привяжем камеру_01 к площадке')
camera_01.SiteId = site.Id
ok = repo.SessionCommit()
if ok:
    session.refresh(camera_01)
print(f'Резульата привязки камеры к сайту = {ok}')
site_camera_count = len(site.Cameras)
print(f'к сайту привязано {site_camera_count} кам.')

if site_camera_count > 0:
    print_message('Отвяжем камеры от площадки')
    for camera in site.Cameras:
        camera.Site = None
        session.refresh(camera)
    ok = repo.SessionCommit()
    print(f'Результат отвязки камеры от площадки = {ok}')

print_message('Привяжем камеры к пользователям')
ok = repo.AddUserCamera(user_01, camera_01)
print(f'Результат привязки камеры к пользоателю = {ok}')

print(f'Количество камер привязанных к пользователю: {len(user_01.Cameras)}')
print(f'Количество пользователей имеющих доступ к камере: {len(camera_01.Users)}')

print_message('Удаление привязки камеры к пользоателю')
ok = repo.DelUserCamera(user_01, camera_01)
print(f'Результат удаления привязки камеры к пользователю = {ok}')

print_message('Удалить поьзователей bea@hotbox.ru, dou@mail.ru')
ok = repo.DelUser('bea@hotbox.ru')
print(f'Результат удаления bea@hotbox.ru = {ok}')
ok = repo.DelUser('dou@mail.ru')
print(f'Результат удаления dou@mail.ru = {ok}')

if ok:
    ClearModelCameras(model_01)
    ClearCustomerCameras(customer)
    ClearModelCameras(model_02)

print_message('удалить модели видеокамер')
ok = repo.DelCameraModel('sony_model_01')
print(f'результат удаления модели sony_model_01 = {ok}')
ok = repo.DelCameraModel('sony_model_02')
print(f'результат удаления модели sony_model_02 = {ok}')
if ok:
    print_message('Удалить бренды')
    ok = repo.DelCameraBrand('Sony')
    print(f'Результат удаления бредна Sony = {ok}')

DelSiteEx('Стройка века')
DelCustomerEx('Profiteam')

session.close()
