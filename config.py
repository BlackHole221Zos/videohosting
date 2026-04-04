# config.py

import os
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Секретный ключ для сессий
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vidsphere-super-secret-key-2024'

    # База данных SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'vidsphere.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Папка для загрузок
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')

    # Максимальный размер файла (100 MB)
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

    # Разрешённые расширения
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # ============ НАСТРОЙКИ EMAIL ============

    # ============ НАСТРОЙКИ EMAIL ============

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')