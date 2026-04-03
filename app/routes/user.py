# app/routes/user.py

from flask import Blueprint, render_template, redirect, url_for, flash, g, request, abort
from app.extensions import db
from app.models import User, Video
from app.forms import ProfileEditForm
from app.utils.decorators import login_required
from app.utils.helpers import save_avatar

user_bp = Blueprint('user', __name__)


# ============ ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ============

@user_bp.route('/user/<username>')
def profile(username):
    """Страница профиля"""

    user = User.query.filter_by(username=username).first_or_404()
    videos = Video.query.filter_by(user_id=user.id).order_by(Video.created_at.desc()).all()

    # Проверка подписки
    is_following = False
    if g.user and g.user.id != user.id:
        is_following = g.user.is_following(user)

    return render_template('user/profile.html',
                           profile_user=user,
                           videos=videos,
                           is_following=is_following
                           )


# ============ РЕДАКТИРОВАНИЕ ПРОФИЛЯ ============

@user_bp.route('/user/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit(username):
    """Редактирование профиля"""

    user = User.query.filter_by(username=username).first_or_404()

    # Только владелец может редактировать
    if g.user.id != user.id:
        abort(403)

    form = ProfileEditForm(user.username, user.email)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data.lower()
        user.bio = form.bio.data or ''

        # Аватар
        if form.avatar.data:
            avatar_filename = save_avatar(form.avatar.data, user.username)
            if avatar_filename:
                user.avatar = avatar_filename

        db.session.commit()

        flash('Профиль обновлён!', 'success')
        return redirect(url_for('user.profile', username=user.username))

    # Заполняем форму текущими данными
    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.bio.data = user.bio

    return render_template('user/edit.html', form=form, profile_user=user)


# ============ ПОДПИСАТЬСЯ ============

@user_bp.route('/user/<username>/follow', methods=['POST'])
@login_required
def follow(username):
    """Подписаться на пользователя"""

    user = User.query.filter_by(username=username).first_or_404()

    if user.id == g.user.id:
        flash('Нельзя подписаться на себя', 'warning')
        return redirect(url_for('user.profile', username=username))

    g.user.follow(user)
    db.session.commit()

    flash(f'Вы подписались на {user.username}!', 'success')
    return redirect(url_for('user.profile', username=username))


# ============ ОТПИСАТЬСЯ ============

@user_bp.route('/user/<username>/unfollow', methods=['POST'])
@login_required
def unfollow(username):
    """Отписаться от пользователя"""

    user = User.query.filter_by(username=username).first_or_404()

    g.user.unfollow(user)
    db.session.commit()

    flash(f'Вы отписались от {user.username}', 'info')
    return redirect(url_for('user.profile', username=username))


# ============ ЛЕНТА ПОДПИСОК ============

@user_bp.route('/subscriptions')
@login_required
def subscriptions():
    """Лента видео от авторов на которых подписан"""

    # ID авторов на которых подписан
    following_ids = [u.id for u in g.user.following.all()]

    if following_ids:
        videos = Video.query.filter(
            Video.user_id.in_(following_ids)
        ).order_by(Video.created_at.desc()).limit(50).all()
    else:
        videos = []

    return render_template('user/subscriptions.html', videos=videos)