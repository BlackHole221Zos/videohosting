# app/utils/decorators.py

from functools import wraps
from flask import g, redirect, url_for, flash, abort


def login_required(f):
    """
    Декоратор: требует авторизации.
    Если пользователь не залогинен — редирект на страницу входа.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('Войдите в аккаунт для доступа к этой странице', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Декоратор: требует прав администратора.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('Войдите в аккаунт', 'warning')
            return redirect(url_for('auth.login'))
        if not g.user.is_admin():
            flash('Доступ запрещён. Требуются права администратора.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def moderator_required(f):
    """
    Декоратор: требует прав модератора или администратора.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('Войдите в аккаунт', 'warning')
            return redirect(url_for('auth.login'))
        if not g.user.is_moderator():
            flash('Доступ запрещён. Требуются права модератора.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function