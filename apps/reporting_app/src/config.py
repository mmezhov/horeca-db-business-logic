import os

class Config:
    # Конфигурация для SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'postgresql://maksim:dfjWI234mso@horeca-horeca_db_service-1/horeca_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Другие настройки приложения Flask
    SECRET_KEY = 'your_secret_key'
