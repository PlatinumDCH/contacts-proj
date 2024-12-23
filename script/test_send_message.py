import asyncio
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.config.configurate import settings

# Конфигурация сервера SMTP
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,  # Ваш email
    MAIL_PASSWORD=settings.MAIL_PASSWORD,  # Ваш пароль
    MAIL_PORT=settings.MAIL_PORT,  # Порт для SMTP
    MAIL_SERVER=settings.MAIL_SERVER,  # SMTP-сервер
    MAIL_FROM=settings.MAIL_USERNAME,  # Отправитель
    MAIL_FROM_NAME="Contact Server",  # Имя отправителя
    MAIL_STARTTLS=False,  # Отключено STARTTLS
    MAIL_SSL_TLS=True,  # Включен SSL/TLS
    USE_CREDENTIALS=True,  # Использовать аутентификацию
    VALIDATE_CERTS=True,  # Проверка сертификатов
    # TEMPLATE_FOLDER=Path(__file__).resolve().parent / "templates",  # Папка с шаблонами
)


async def send_test_email():
    """Отправка тестового письма."""
    fm = FastMail(conf)

    # Создаем сообщение
    message = MessageSchema(
        subject="Test Email",  # Тема письма
        recipients=["dimacheban23@meta.ua"],  # Кому отправить
        body="<h1>This is a test email</h1><p>Hello, this is a test email sent using FastMail.</p>",
        subtype=MessageType.html,  # Указываем HTML-тип
    )

    # Отправляем сообщение
    try:
        await fm.send_message(message)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Запускаем отправку
if __name__ == "__main__":
    asyncio.run(send_test_email())
