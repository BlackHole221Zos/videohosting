# app/routes/auth.py

from flask import Blueprint, render_template, redirect, url_for, flash, session, g
from app.extensions import db
from app.models import User
from app.forms import RegisterForm, LoginForm
from flask_mail import Message
from app.extensions import mail
from app.models import PasswordResetToken
from app.forms import ForgotPasswordForm, ResetPasswordForm

auth_bp = Blueprint('auth', __name__)


# ============ РЕГИСТРАЦИЯ ============

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""

    # Если уже залогинен — на главную
    if g.user:
        return redirect(url_for('main.index'))

    form = RegisterForm()

    if form.validate_on_submit():
        # Создаём пользователя
        user = User(
            username=form.username.data,
            email=form.email.data.lower()
        )
        user.set_password(form.password.data)

        # Сохраняем в БД
        db.session.add(user)
        db.session.commit()

        # Сразу авторизуем пользователя
        session.clear()
        session['user_id'] = user.id

        flash(f'Добро пожаловать в VidSphere, {user.username}! 🚀', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html', form=form)


# ============ ВХОД ============

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""

    # Если уже залогинен — на главную
    if g.user:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        # Ищем пользователя
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            # Успешный вход — сохраняем в сессию
            session.clear()
            session['user_id'] = user.id

            flash(f'С возвращением, {user.username}!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')

    return render_template('auth/login.html', form=form)


# ============ ВЫХОД ============

@auth_bp.route('/logout')
def logout():
    """Выход из аккаунта"""
    session.clear()
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('main.index'))


# ============ ВОССТАНОВЛЕНИЕ ПАРОЛЯ ============

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Запрос на восстановление пароля"""

    if g.user:
        return redirect(url_for('main.index'))

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        email = form.email.data.lower()
        user = User.query.filter_by(email=email).first()

        if user:
            # Создаём токен
            token = PasswordResetToken.create_for_user(user)

            # Формируем ссылку
            reset_url = url_for('auth.reset_password', token=token.token, _external=True)

            # Отправляем email
            try:
                msg = Message(
                    subject='Восстановление пароля VidSphere',
                    recipients=[user.email],
                    body=f'''Здравствуйте, {user.username}!

Вы запросили восстановление пароля на VidSphere.

Перейдите по ссылке для установки нового пароля:
{reset_url}

Ссылка действительна в течение 1 часа.

Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо.

---
VidSphere — Космический видеохостинг 🌌
'''
                )
                mail.send(msg)

                flash(f'Письмо с инструкцией отправлено на {email}', 'success')
                return redirect(url_for('auth.login'))

            except Exception as e:
                flash('Ошибка отправки письма. Попробуйте позже.', 'danger')
                print(f"Email error: {e}")
        else:
            # Не говорим что пользователь не найден (безопасность)
            flash(f'Если email {email} зарегистрирован, на него отправлено письмо', 'info')
            return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Установка нового пароля по токену"""

    if g.user:
        return redirect(url_for('main.index'))

    # Проверяем токен
    user = PasswordResetToken.verify_token(token)

    if not user:
        flash('Недействительная или истёкшая ссылка для восстановления пароля', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        # Устанавливаем новый пароль
        user.set_password(form.password.data)

        # Удаляем использованный токен
        PasswordResetToken.query.filter_by(token=token).delete()

        db.session.commit()

        flash('Пароль успешно изменён! Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form, token=token)