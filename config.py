# config.py

import os

# Корневая папка проекта
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Конфигурация приложения"""

    # Секретный ключ для сессий и CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vidsphere-secret-key-change-in-production'

    # База данных SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'vidsphere.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Папка для загрузок (аватары, видео, превью)
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')

    # Максимальный размер файла: 100 MB
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024