# app/routes/auth.py

from flask import Blueprint, render_template, redirect, url_for, flash, session, g
from app.extensions import db
from app.models import User
from app.forms import RegisterForm, LoginForm

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

        flash(f'Добро пожаловать, {user.username}! Теперь войдите в аккаунт.', 'success')
        return redirect(url_for('auth.login'))

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