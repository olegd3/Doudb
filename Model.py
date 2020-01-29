# Model of doudb
from datetime import datetime
from sqlalchemy import Column, ForeignKey
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.types import Integer, String, DateTime, Boolean
import sqlalchemy.orm
from sqlalchemy.orm import relationship, Session
import ipaddress



base = declarative_base()
class CameraBrand(base):
    session: sqlalchemy.orm.Session
    __tablename__ = "camerabrand"

    Id = Column(Integer, primary_key=True)
    BrandName = Column(String(255), nullable=False)
    Models = relationship("CameraModel", lazy=False, back_populates="Brand")

    def __init__(self, barnd_name: str):
        self.BrandName = barnd_name

    def __repr__(self):
        return f'Id = {self.Id}; BrandName = \"{self.BrandName}\"'

    def AddCameraModel(self, camera_name: str) -> 'CameraModel':
        model: CameraModel = CameraModel(self.Id, camera_name)
        self.Models.append(model)
        return model

    def GetCameraModel(self, camera_name: str) -> 'CameraModel':
        model: CameraModel = next((x for x in self.Models if x.CameraName == camera_name), None)
        return model

    def RemoveCameraModel(self, cameraName: str):
        model: CameraModel = self.GetCameraModel(cameraName)
        if model is not None:
            self.Models.remove(model)
            if model.Id is not None:
                CameraBrand.session.delete(model)



class CameraModel(base):
    session: sqlalchemy.orm.Session
    __tablename__ = "cameramodel"

    Id = Column(Integer, primary_key=True)
    BrandId = Column(Integer, ForeignKey('camerabrand.Id'))
    CameraName = Column(String, nullable=False)
    Brand = relationship("CameraBrand", back_populates="Models")
    Cameras = relationship("Camera", lazy=False, back_populates="Model")
    Properties = relationship("ModelProperty", lazy=False, back_populates="Model")

    def __init__(self, brandId: int, cameraName: str = 'General'):
        self.BrandId = brandId
        self.CameraName = cameraName

    def __repr__(self):
        return f'Id = {self.Id}; BrandId = {self.BrandId}; CameraName = \"{self.CameraName}\", , Brand={self.Brand.BrandName}'

    def GetProprerty(self, prop: str) -> 'ModelProperty':
        model_property: ModelProperty = next((x for x in self.Properties if x.Param == prop), None)
        return  model_property

    def AddProperty(self, prop: str, val: str) -> 'ModelProperty':
        model_property: ModelProperty = self.GetProprerty(prop)
        if model_property is not None:
            model_property.Value = val
        else:
            model_property = ModelProperty(self.Id, prop, val)
            self.Properties.append(model_property)
        return model_property

    def RemoveProperty(self, prop: str):
        model_property: ModelProperty = self.GetProprerty(prop)
        if model_property is not None:
            self.Properties.remove(model_property)
            CameraModel.session.delete(model_property)


class ModelProperty(base):
    session: sqlalchemy.orm.Session
    __tablename__ = "modelproperty"

    ModelId = Column(Integer, ForeignKey("cameramodel.Id"), primary_key=True)
    Param = Column(String(255), primary_key=True)
    Value = Column(String(255), nullable=False)
    Model = relationship("CameraModel", back_populates="Properties")

    def __init__(self, model_id: int, param: str, val: str):
        self.ModelId = model_id
        self.Param = param
        self.Value = val

    def __repr__(self):
        return f'Model ={self.Model.CameraName}; Model_id = {self.ModelId}; Param=\"{self.Param}\"; Value=\"{self.Value}\"'



class Customer(base):
    session: sqlalchemy.orm.Session
    __tablename__ = "customer"

    Id = Column(Integer, primary_key=True)
    CustomerName = Column(String(255), nullable=False)
    CreationDate = Column(DateTime, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    Users = relationship("User", lazy=False, back_populates="Customer")
    Cameras = relationship("Camera", lazy=False, back_populates="Customer")

    def __init__(self, customerName: str):
        self.CustomerName = customerName
        self.CreationDate = datetime.now()
        self.IsActive = True

    def __repr__(self):
        return f'Id = {self.Id}; CustomerName = \"{self.CustomerName}\"; ' \
               f'CreationDate = {self.CreationDate}, IsActive = {self.IsActive}'

    def AddUser(self, login: str) -> 'User':
        user: User = User(customer_id=self.Id, login=login)
        self.Users.append(user)
        Customer.session.add(user)
        return user

    def GetUser(self, login: str) -> 'User':
        user: User = next((x for x in self.Users if x.Login == login), None)
        return user

    def RemoveUser(self, login: str):
        user: User = self.GetUser(login)
        if user is not None:
            try:
                if user.telegram is not None:
                    User.session.delete(user.telegram)
                self.Users.remove(user)
                Customer.session.delete(user)
            except InvalidRequestError:
                pass



class User(base):
    session: sqlalchemy.orm.Session
    __tablename__ = "user"

    Login = Column(String(255), primary_key=True)
    CustomerId = Column(Integer, ForeignKey('customer.Id'))
    Customer = relationship("Customer", back_populates="Users")
    _telegram = relationship("Telegram", uselist=False)
    Cameras = relationship("UserCamera", back_populates="Camera")

    @property
    def telegram(self):
        return self._telegram

    @telegram.setter
    def telegram(self, value: str):
        if value is not None and self._telegram is None:
            self._telegram = Telegram(self.Login, value)
            Telegram.session.add(self._telegram)
        elif value is not None and self._telegram is not None:
            Telegram.session.delete(self._telegram)
            self._telegram = Telegram(self.Login, value)
            #Telegram.session.add(self._telegram)
        elif value is None and self._telegram is not None:
            Telegram.session.delete(self._telegram)
            self._telegram = None

    def __init__(self, login: str, customer_id: int):
        self.Login = login
        self.CustomerId = customer_id

    def __repr__(self):
        return f'Login=\"{self.Login}\"; CustomerId={self.CustomerId}; ' \
               f'Customer={self.Customer.CustomerName}; Telegram={self._telegram}'



class Telegram(base):
    session: sqlalchemy.orm.Session
    __tablename__ = "telegram"

    Login = Column(String(255), ForeignKey('user.Login'), primary_key=True )
    TelegramId = Column(String(255), nullable=False)

    def __init__(self, login: str, telegram: str):
        self.Login = login
        self.TelegramId = telegram

    def __repr__(self):
        return f'\"{self.TelegramId}\"'


class Site(base):
    session: sqlalchemy.orm.Session
    __tablename__ = "site"

    Id = Column(Integer, primary_key=True)
    SiteName = Column(String(255), nullable=False)
    Address = Column(String(255), nullable=False)
    Cameras  = relationship("Camera", lazy=False, back_populates="Site")

    def __init__(self, site_name="unknown", addres="unknown"):
        self.SiteName = site_name
        self.Address = addres

    def __repr__(self):
        return  f'Id = {self.Id}; SiteName = \"{self.SiteName}\"; Addres = \"{self.Address}\"'


class Camera(base):
    session: sqlalchemy.orm.Session
    __tablename__ = "camera"

    __mapper_args__ = {
        'confirm_deleted_rows': False
    }

    Id = Column(Integer, primary_key=True)
    ModelId = Column(Integer, ForeignKey('cameramodel.Id'), nullable=False)
    Model = relationship("CameraModel", back_populates="Cameras")
    CustomerId = Column(Integer, ForeignKey('customer.Id'), nullable=False)
    Customer = relationship("Customer", back_populates="Cameras")
    SiteId = Column(Integer, ForeignKey('site.Id'), nullable=True)
    Site = relationship("Site", back_populates="Cameras")
    CameraLogin = Column(String(255))
    CameraPassword = Column(String(255))
    _ip = Column("IP", Integer)
    Port = Column(Integer)
    Users = relationship("UserCamera", back_populates="User")

    @property
    def ip(self):
        if self._ip is not None:
            return ipaddress.ip_address(self._ip)
        return self._ip

    @ip.setter
    def ip(self, value):
        if value is None:
            self._ip=value
        if type(value) is ipaddress.IPv4Address or type(value) is ipaddress.IPv6Address:
            self._ip=int(value)

    def __init__(self, model_id: int, customer_id: int ):
        self.ModelId = model_id
        self.CustomerId = customer_id

    def __repr__(self):
        return f'Id = {self.Id}; Brand = \"{self.Model.Brand.BrandName}\"; Model =\"{self.Model.CameraName}\"; ' \
               f'Login =\"{self.CameraLogin}\"; Pwd = \"{self.CameraPassword}\"; IP:Port = {self.ip}:{self.Port}'


class UserCamera(base):
    session: sqlalchemy.orm.Session
    __tablename__ = "usercamera"

    CameraId = Column('Camera_Id', Integer, ForeignKey("camera.Id"), primary_key=True)
    Login = Column('Login', String(255), ForeignKey("user.Login"), primary_key=True)
    User = relationship("Camera", back_populates="Users")
    Camera = relationship("User", back_populates="Cameras")

    def __init__(self, login: str, camera_id: int):
        self.Login = login
        self.CameraId = camera_id
