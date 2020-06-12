from Model import CameraBrand, CameraModel,  Customer, User, Site, Camera, UserCamera, ModelProperty, Telegram
from typing import List
import sqlalchemy.orm
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.ext.declarative import declarative_base


class Repo(object):

    def __init__(self):
        connStr = 'mysql+mysqlconnector://root:4Belki8Sov@localhost:3306/doudb'
        engine = create_engine(connStr, echo=False)
        Base = declarative_base()
        Base.metadata.create_all(engine, checkfirst=True)
        self.session = self.CreateSession(engine)
        CameraBrand.session = self.session
        CameraModel.session = self.session
        Customer.session = self.session
        User.session = self.session
        Site.session = self.session
        Camera.session = self.session
        ModelProperty.session = self.session
        Telegram.session = self.session

    def CreateSession(self, engine) -> sqlalchemy.orm.Session:
        Session = sqlalchemy.orm.sessionmaker(expire_on_commit=False)
        Session.configure(bind=engine)
        session: sqlalchemy.orm.Session = Session()
        return session

    def SessionCommit(self) -> bool:
        ok: bool = True
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            ok = False
        except FlushError:
            ok = False
        return ok

    def GetAllCameraBrands(self) -> List[CameraBrand]:
        brands = self.session.query(CameraBrand).all()
        ok: bool = self.SessionCommit()
        return brands

    def GetCameraBrand(self, brandname: str) -> CameraBrand:
        camerabrand: CameraBrand = self.session.query(CameraBrand).filter_by(BrandName=brandname).first()
        self.SessionCommit()
        return camerabrand

    def AddCameraBrand(self, brandname: str) -> CameraBrand:
        brand = CameraBrand(brandname)
        self.session.add(brand)
        ok: bool = self.SessionCommit()
        if not ok:
            brand = None
        return brand

    def DelCameraBrand(self, brandname: str) -> bool:
        brand = self.GetCameraBrand(brandname)
        ok: bool = False
        if brand is not None:
            self.session.delete(brand)
            ok = self.SessionCommit()
        return ok

    def GetCameraModel(self, model_name: str) -> CameraModel:
        model: CameraModel = self.session.query(CameraModel).filter_by(CameraName=model_name).first()
        return model

    def DelCameraModel(self, model_name: str) -> bool:
        model: CameraModel = self.GetCameraModel(model_name)
        ok: bool = False
        if model is not None:
            self.session.delete(model)
            ok = self.SessionCommit()
        if ok:
            self.session.refresh(model.Brand)
        return ok

    def GetAllCustomers(self) -> List[Customer]:
        customers = self.session.query(Customer).all()
        ok: bool = self.SessionCommit()
        return customers

    def GetCustomer(self, customer_name: str) -> Customer:
        customer: Customer = self.session.query(Customer).filter_by(CustomerName=customer_name).first()
        return customer

    def AddCustomer(self, customer_name: str) -> Customer:
        customer = Customer(customer_name)
        self.session.add(customer)
        ok: bool = self.SessionCommit()
        if not ok:
            customer = None
        return customer

    def DelCustomer(self, customer_name: str) -> bool:
        customer: Customer = self.GetCustomer(customer_name)
        ok: bool = False
        if customer is not None:
            self.session.delete(customer)
            ok = self.SessionCommit()
        return ok

    def GetUser(self, login: str) -> User:
        user: User = self.session.query(User).filter_by(Login=login).first()
        return user

    def DelUser(self, login:str) -> bool:
        ok = False
        user: User = self.GetUser(login)
        if user is not None:
            self.session.delete(user)
            ok = self.SessionCommit()
        if ok:
            self.session.refresh(user.Customer)
        return ok

    def AddSite(self, site_name: str, address: str = '') -> Site:
        site: Site = Site(site_name, address)
        self.session.add(site)
        ok: bool = self.SessionCommit()
        if not ok:
            site = None
        return site

    def GetSite(self, site_name: str) -> Site:
        sites = self.session.query(Site).all()
        site: Site = self.session.query(Site).filter_by(SiteName=site_name).first()
        return site

    def DelSite(self, site_name: str) -> bool:
        site: Site = self.GetSite(site_name)
        ok: bool = False
        if site is not None:
            self.session.delete(site)
            ok = self.SessionCommit()
        return ok

    def AddCamera(self, model: CameraModel, customer: Customer) -> Camera:
        camera: Camera = None
        if (model is not None) and (customer is not None):
            camera = Camera(model_id=model.Id, customer_id=customer.Id)
            self.session.add(camera)
            ok: bool = self.SessionCommit()
            if ok:
                self.session.refresh(model)
                self.session.refresh(customer)
            if not ok:
                camera = None
        return camera

    def DelCamera(self, camera: Camera) -> bool:
        customer: Customer = camera.Customer
        model: CameraModel = camera.Model
        self.session.delete(camera)
        ok: bool = self.SessionCommit()
        if ok:
            self.session.refresh(customer)
            self.session.refresh(model)
        return ok

    def SetCameraIp(self, camera: Camera, ip_address) -> bool:
        camera.ip = ip_address
        ok: bool = self.SessionCommit()
        return ok

    def AddUserCamera(self, user: User, camera:Camera) -> bool:
        ok: bool = False
        if user is not None and camera is not None:
            user_camera: UserCamera = UserCamera(user.Login, camera.Id)
            self.session.add(user_camera)
            ok = self.SessionCommit()
            if ok:
                self.session.refresh(user)
                self.session.refresh(camera)
        return ok

    def GetUserCamera(self, user: User, camera: Camera) -> UserCamera:
        user_camera: UserCamera = self.session.query(UserCamera).filter_by(Login=user.Login, CameraId=camera.Id).first()
        return user_camera

    def DelUserCamera(self, user: User, camera: Camera) -> bool:
        ok: bool = False
        user_camera: UserCamera = self.GetUserCamera(user, camera)
        if user_camera is not None:
            self.session.delete(user_camera)
            ok = self.SessionCommit()
            if ok:
                self.session.refresh(user)
                self.session.refresh(camera)
        return ok
