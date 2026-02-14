# config stuff
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # base settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///collabstr.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False
    
    # JWT Configuration
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 168))  # 7 days default
    JWT_ALGORITHM = 'HS256'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    DEBUG = False


def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'testing':
        return TestingConfig()
    elif env == 'production':
        return ProductionConfig()
    return DevelopmentConfig()
