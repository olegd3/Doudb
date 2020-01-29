# Тестируем связь CameraBrand c CameraModel
from Model import CameraBrand, CameraModel
from typing import List
from Repo import Repo



def PrintAll(list: List):
    for item in list:
        print(f'{item=}')

def print_message(message: str, blank: bool = True):
    if blank:
        print('*'*20 +f' {message} '+ '*'*20)
    else:
        print('*' * 20 + f'{message}' + '*' * 20)

def AddBrandModel(brand: CameraBrand, model_name: str) -> CameraModel:
    print_message('Добавить модель камеры')
    model: CameraModel = brand.AddCameraModel(model_name)
    ok: bool = repo.SessionCommit()
    if not ok:
        model = None
    print(f'результат добавления = {ok}')
    print(model)
    return model

def DelBrandModel(brand: CameraModel, model_name: str):
    print_message('Удалить модель камеры')
    brand.RemoveCameraModel(model_name)
    ok: bool  = repo.SessionCommit()
    print(f'результат удаления = {ok}')

def CreateCameraBrandEx(brand_name: str ):
    print_message(f'Добавить бранд {brand_name}')
    brand: CameraBrand = repo.AddCameraBrand(brand_name)
    print(brand)

def DelCameraBrandEx(brand_name: str):
    print_message(f'Удалить бренд {brand_name}')
    ok = repo.DelCameraBrand(brand_name)
    print(f'Результат удаления = {ok}')

def SimpleUpdate() -> bool:
    p = ('Panasonic', 'Banasonic')
    brand = repo.GetCameraBrand(p[0])
    if brand is None:
        p = (p[1], p[0])
        brand = repo.GetCameraBrand(p[0])
    brand.BrandName = p[1]
    ok: bool = repo.SessionCommit()
    return ok


# connect and create session
repo = Repo()
session = repo.session

brands: List[CameraBrand] = repo.GetAllCameraBrands();
if len(brands) == 0:
    CreateCameraBrandEx('Sony')
    CreateCameraBrandEx('JVC')
    CreateCameraBrandEx('Panasonic')
    CreateCameraBrandEx('BBK')
    CreateCameraBrandEx('Google')
    brands = repo.GetAllCameraBrands()
print_message('Все бренды')
PrintAll(brands)

ok: bool = False
brand: CameraBrand = None

print_message('Выбрать бренд')
brand = repo.GetCameraBrand('Google')
if brand is None:
    CreateCameraBrandEx('Google')
print(brand)

#print_message('Изменяем наименование бренда Panasonic <-> Banasonic')
#ok = SimpleUpdate()
#print(f'Результат изменения ok = {ok}')

model: CameraModel = AddBrandModel(brand, 'Google_Model_01')
if model is None:
    model = brand.GetCameraModel('Google_Model_01')
print_message('Получим доступ к бренду из модели')
print(model.Brand)
DelBrandModel(brand, 'Google_Model_01')

DelCameraBrandEx('Google')
DelCameraBrandEx('BBK')
DelCameraBrandEx('Panasonic')
DelCameraBrandEx('JVC')
DelCameraBrandEx('Sony')

session.close()