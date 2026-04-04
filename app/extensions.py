# app/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

# Инициализация расширений
db = SQLAlchemy()
mail = Mail()