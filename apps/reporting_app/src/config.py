import os

class Config:
    # Конфигурация для SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'postgresql://maksim:dfjWI234mso@horeca-horeca_db_service-1/horeca_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Для API
    TOKEN = 'KUbnv874Dkfg'

    # Для тестов
    API_URL = "https://horeca.turboapi.ru/api"
