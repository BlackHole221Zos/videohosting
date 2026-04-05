# app/routes/user.py

from flask import Blueprint, render_template, redirect, url_for, flash, g, request, abort, jsonify
from app.extensions import db
from app.models import User, Video, WatchHistory
from app.forms import ProfileEditForm
from app.utils.decorators import login_required
from app.utils.helpers import save_avatar
from datetime import datetime, timedelta


user_bp = Blueprint('user', __name__)


# ============ ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ============

@user_bp.route('/user/<username>')
def profile(username):
    """Страница профиля"""

    user = User.query.filter_by(username=username).first_or_404()

    # Показываем только публичные видео (если не сам автор)
    if g.user and g.user.id == user.id:
        # Автор видит все свои видео
        videos = Video.query.filter_by(user_id=user.id) \
            .order_by(Video.created_at.desc()).all()
    else:
        # Остальные — только публичные
        videos = Video.query.filter_by(user_id=user.id, visibility='public') \
            .order_by(Video.created_at.desc()).all()

    is_following = False
    if g.user and g.user.id != user.id:
        is_following = g.user.is_following(user)

    return render_template('user/profile.html',
                           profile_user=user,
                           videos=videos,
                           is_following=is_following)


# ============ РЕДАКТИРОВАНИЕ ПРОФИЛЯ ============

@user_bp.route('/user/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit(username):
    """Редактирование профиля"""

    user = User.query.filter_by(username=username).first_or_404()

    if g.user.id != user.id:
        abort(403)

    form = ProfileEditForm(user.username, user.email)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data.lower()
        user.bio = form.bio.data or ''

        if form.avatar.data:
            avatar_filename = save_avatar(form.avatar.data, user.username)
            if avatar_filename:
                user.avatar = avatar_filename

        db.session.commit()
        flash('Профиль обновлён!', 'success')
        return redirect(url_for('user.profile', username=user.username))

    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.bio.data = user.bio

    return render_template('user/edit.html', form=form, profile_user=user)


# ============ ПОДПИСАТЬСЯ (AJAX) ============

@user_bp.route('/user/<username>/follow', methods=['POST'])
@login_required
def follow(username):
    """Подписаться"""
    user = User.query.filter_by(username=username).first_or_404()

    if user.id == g.user.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Нельзя подписаться на себя'}), 400
        flash('Нельзя подписаться на себя', 'warning')
        return redirect(url_for('user.profile', username=username))

    g.user.follow(user)
    db.session.commit()

    # AJAX запрос
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'is_following': True,
            'followers_count': user.followers_count()
        })

    flash(f'Вы подписались на {user.username}!', 'success')
    return redirect(request.referrer or url_for('user.profile', username=username))


# ============ ОТПИСАТЬСЯ (AJAX) ============

@user_bp.route('/user/<username>/unfollow', methods=['POST'])
@login_required
def unfollow(username):
    """Отписаться"""
    user = User.query.filter_by(username=username).first_or_404()

    g.user.unfollow(user)
    db.session.commit()

    # AJAX запрос
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'is_following': False,
            'followers_count': user.followers_count()
        })

    flash(f'Вы отписались от {user.username}', 'info')
    return redirect(request.referrer or url_for('user.profile', username=username))

# ============ ПОДПИСКИ (КАНАЛЫ С ВИДЕО) ============

@user_bp.route('/subscriptions')
@login_required
def subscriptions():
    """Каналы на которые подписан с их последними видео"""

    channels = g.user.following.order_by(User.username).all()

    channels_data = []
    for channel in channels:
        # Только публичные видео
        recent = channel.videos.filter_by(visibility='public') \
            .order_by(Video.created_at.desc()).limit(4).all()
        channels_data.append({
            'user': channel,
            'recent_videos': recent
        })

    return render_template('user/subscriptions.html', channels_data=channels_data)


# ============ ИСТОРИЯ ПРОСМОТРОВ ============

@user_bp.route('/history')
@login_required
def history():
    """История просмотров с группировкой по датам"""

    history_items = WatchHistory.query.filter_by(user_id=g.user.id) \
        .order_by(WatchHistory.watched_at.desc()) \
        .limit(100).all()

    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)

    grouped = {
        'today': [],
        'yesterday': [],
        'this_week': [],
        'earlier': []
    }

    for item in history_items:
        d = item.watched_at.date()
        if d == today:
            grouped['today'].append(item)
        elif d == yesterday:
            grouped['yesterday'].append(item)
        elif d > week_ago:
            grouped['this_week'].append(item)
        else:
            grouped['earlier'].append(item)

    return render_template('user/history.html', grouped=grouped)


# ============ УДАЛИТЬ ИЗ ИСТОРИИ ============

@user_bp.route('/history/<int:history_id>/delete', methods=['POST'])
@login_required
def delete_history_item(history_id):
    """Удалить одну запись"""
    item = WatchHistory.query.get_or_404(history_id)

    if item.user_id != g.user.id:
        abort(403)

    db.session.delete(item)
    db.session.commit()
    flash('Удалено из истории', 'info')
    return redirect(url_for('user.history'))


# ============ ОЧИСТИТЬ ИСТОРИЮ ============

@user_bp.route('/history/clear', methods=['POST'])
@login_required
def clear_history():
    """Очистить всю историю"""
    WatchHistory.query.filter_by(user_id=g.user.id).delete()
    db.session.commit()
    flash('История очищена', 'success')
    return redirect(url_for('user.history'))