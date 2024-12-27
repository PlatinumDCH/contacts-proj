from app.services.auth_serv import AuthService
from app.services.jwt_serv import JWTService
from app.services.password_serv import PasswordService
from app.services.email_serv import EmailService


class ServiceFacade:
    def __init__(self):
        self._password_service = PasswordService()
        self._jwt_service = JWTService()
        self._auth_service = AuthService()
        self._email_service = EmailService()

    @property
    def password(self):
        return self._password_service

    @property
    def jwt(self):
        return self._jwt_service

    @property
    def auth(self):
        return self._auth_service

    @property
    def email(self):
        return self._email_service

    def __getattr__(self, item):
        """если метод не найден пробуем найти его в одном из сервисов"""
        for service in (
            self._password_service,
            self._jwt_service,
            self._auth_service,
            self._email_service,
        ):
            if hasattr(service, item):
                return getattr(service, item)
        raise ArithmeticError(f"{self.__class__.__name__} has no atribure {item}")


service = ServiceFacade()
