# app/__init__.py

import os
from flask import Flask, g, session
from config import Config
from app.extensions import db, mail


def create_app(config_class=Config):
    """Фабрика приложения Flask"""

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация расширений
    db.init_app(app)
    mail.init_app(app)

    # Создание папок для загрузок
    upload_paths = [
        os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'),
        os.path.join(app.config['UPLOAD_FOLDER'], 'videos'),
        os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails')
    ]
    for path in upload_paths:
        os.makedirs(path, exist_ok=True)

    # Папка для документов
    os.makedirs(os.path.join(app.static_folder, 'docs'), exist_ok=True)

    # Загрузка текущего пользователя
    @app.before_request
    def load_user():
        from app.models import User
        user_id = session.get('user_id')
        if user_id:
            g.user = db.session.get(User, user_id)
        else:
            g.user = None

    # Контекст для шаблонов
    @app.context_processor
    def inject_user():
        return dict(user=g.user if hasattr(g, 'user') else None)

    # Регистрация Blueprint'ов
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.video import video_bp
    from app.routes.user import user_bp
    from app.routes.search import search_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(search_bp)

    # Инициализация БД
    from app.models import init_db
    init_db(app)

    # Генерация PDF (безопасно)
    try:
        with app.app_context():
            from app.utils.pdf_generator import generate_legal_pdfs
            generate_legal_pdfs()
    except Exception as e:
        print(f'⚠️ PDF не сгенерированы: {e}')

    return app