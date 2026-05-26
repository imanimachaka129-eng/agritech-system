import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'agrismart_secret_2026'
    DATABASE = os.path.join(BASE_DIR, 'agrismart.db')
    DEBUG = True