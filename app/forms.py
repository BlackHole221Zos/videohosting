import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from app.models import User

# ============ ВАЛИДАТОР ПАРОЛЯ ============

def strong_password(form, field):
    """
    Проверяет надёжность пароля:
    - Минимум 6 символов
    - Хотя бы одна цифра
    - Хотя бы одна строчная буква
    - Хотя бы одна заглавная буква
    """
    password = field.data

    if len(password) < 6:
        raise ValidationError('Минимум 6 символов')

    if not re.search(r'\d', password):
        raise ValidationError('Нужна хотя бы одна цифра')

    if not re.search(r'[a-z]', password):
        raise ValidationError('Нужна хотя бы одна строчная буква')

    if not re.search(r'[A-Z]', password):
        raise ValidationError('Нужна хотя бы одна заглавная буква')


# ============ ФОРМА РЕГИСТРАЦИИ ============

class RegisterForm(FlaskForm):
    """Форма регистрации нового пользователя"""

    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Введите имя пользователя'),
        Length(min=3, max=80, message='От 3 до 80 символов')
    ])

    email = StringField('Email', validators=[
        DataRequired(message='Введите email'),
        Email(message='Некорректный email')
    ])

    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль'),
        strong_password
    ])

    password_confirm = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Подтвердите пароль'),
        EqualTo('password', message='Пароли не совпадают')
    ])

    def validate_username(self, field):
        """Проверяет уникальность имени"""
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Это имя уже занято')

    def validate_email(self, field):
        """Проверяет уникальность email"""
        user = User.query.filter_by(email=field.data.lower()).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован')


# ============ ФОРМА ВХОДА ============

class LoginForm(FlaskForm):
    """Форма входа"""

    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Введите имя пользователя')
    ])

    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль')
    ])


# ============ ФОРМА ЗАГРУЗКИ ВИДЕО ============

class VideoUploadForm(FlaskForm):
    """Форма загрузки видео"""

    title = StringField('Название', validators=[
        DataRequired(message='Введите название'),
        Length(min=3, max=200, message='От 3 до 200 символов')
    ])

    description = TextAreaField('Описание', validators=[
        Length(max=2000, message='Максимум 2000 символов')
    ])

    video = FileField('Видео файл', validators=[
        FileRequired(message='Выберите видео'),
        FileAllowed(['mp4', 'avi', 'mov', 'mkv', 'webm'], 'Только видео файлы!')
    ])

    mood = SelectField('Настроение', choices=[
        ('inspiration', '✨ Вдохновение'),
        ('laugh', '😂 Смех'),
        ('knowledge', '🧠 Знания'),
        ('peace', '🌸 Покой'),
        ('adrenaline', '⚡ Адреналин')
    ], validators=[
        DataRequired(message='Выберите настроение')
    ])

    tags = StringField('Теги', validators=[
        Length(max=500, message='Максимум 500 символов')
    ])


# ============ ФОРМА КОММЕНТАРИЯ ============

class CommentForm(FlaskForm):
    """Форма добавления комментария"""

    text = TextAreaField('Комментарий', validators=[
        DataRequired(message='Введите комментарий'),
        Length(min=1, max=1000, message='От 1 до 1000 символов')
    ])


# ============ ФОРМА РЕДАКТИРОВАНИЯ ПРОФИЛЯ ============

class ProfileEditForm(FlaskForm):
    """Форма редактирования профиля"""

    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Введите имя'),
        Length(min=3, max=80, message='От 3 до 80 символов')
    ])

    email = StringField('Email', validators=[
        DataRequired(message='Введите email'),
        Email(message='Некорректный email')
    ])

    bio = TextAreaField('О себе', validators=[
        Length(max=500, message='Максимум 500 символов')
    ])

    avatar = FileField('Аватар', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Только изображения!')
    ])

    def __init__(self, original_username, original_email, *args, **kwargs):
        """
        Сохраняем оригинальные значения для проверки уникальности
        (чтобы пользователь мог оставить свои текущие данные)
        """
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, field):
        """Проверяет уникальность (если изменилось)"""
        if field.data != self.original_username:
            user = User.query.filter_by(username=field.data).first()
            if user:
                raise ValidationError('Это имя уже занято')

    def validate_email(self, field):
        """Проверяет уникальность (если изменилось)"""
        if field.data.lower() != self.original_email.lower():
            user = User.query.filter_by(email=field.data.lower()).first()
            if user:
                raise ValidationError('Этот email уже занят')


# ============ ФОРМА ПОИСКА ============

class SearchForm(FlaskForm):
    """Форма поиска"""

    q = StringField('Поиск', validators=[
        Length(max=100, message='Максимум 100 символов')
    ])

    mood = SelectField('Настроение', choices=[
        ('', 'Все настроения'),
        ('laugh', '😂 Смех'),
        ('knowledge', '🧠 Знания'),
        ('peace', '🌸 Покой'),
        ('adrenaline', '⚡ Адреналин'),
        ('inspiration', '✨ Вдохновение')
    ])

    sort = SelectField('Сортировка', choices=[
        ('date', 'По дате'),
        ('views', 'По просмотрам'),
        ('karma', 'По карме')
    ])


# ============ ФОРМА ВОССТАНОВЛЕНИЯ ПАРОЛЯ ============

class ForgotPasswordForm(FlaskForm):
    """Форма запроса восстановления пароля"""

    email = StringField('Email', validators=[
        DataRequired(message='Введите email'),
        Email(message='Некорректный email')
    ])


class ResetPasswordForm(FlaskForm):
    """Форма установки нового пароля"""

    password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Введите пароль'),
        Length(min=6, message='Минимум 6 символов'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$',
               message='Пароль должен содержать заглавные, строчные буквы и цифры')
    ])

    password_confirm = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Подтвердите пароль'),
        EqualTo('password', message='Пароли не совпадают')
    ])