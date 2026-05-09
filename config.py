# config.py

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

basedir = os.path.abspath(os.path.dirname(__file__))

# ✅ Автосоздание instance/
os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lampix-super-secret-key-2025'

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        'sqlite:///' + os.path.join(basedir, 'instance', 'lampix.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 2GB

    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME') or 'noreply@lampix.ru'