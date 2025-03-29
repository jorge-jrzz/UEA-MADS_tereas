from pathlib import Path


db_path = Path('./data/sistema.db').resolve()

class DevelopmentConfig():
    SECRET_KEY = 'application_by_yorch'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    HOST = '0.0.0.0'
    PORT = 5001
