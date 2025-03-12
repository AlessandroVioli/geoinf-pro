import os

class Config:
    SECRET_KEY = os.environ.get('KEY') or '1234567'
    FLASK_ADMIN_SWATCH = 'flatly'#'cerulean'

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:ele1234567@localhost:5432/olulcmaps_dev'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@host:port/database_name'


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}