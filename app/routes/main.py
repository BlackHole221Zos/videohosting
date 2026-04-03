# app/routes/main.py

from flask import Blueprint, render_template, g
from app.models import Video, WatchHistory

main_bp = Blueprint('main', __name__)


# ============ ГЛАВНАЯ СТРАНИЦА ============

@main_bp.route('/')
def index():
    """Главная страница"""

    # Hero карусель — топ 5 по карме
    hero_videos = Video.query.order_by(Video.karma.desc()).limit(5).all()

    # Новые видео
    new_videos = Video.query.order_by(Video.created_at.desc()).limit(12).all()

    # Тренды (сортировка по hot_score)
    all_videos = Video.query.all()
    trending_videos = sorted(all_videos, key=lambda v: v.hot_score(), reverse=True)[:12]

    # Видео по настроениям
    moods_data = {
        'laugh': {'emoji': '😂', 'name': 'Смех'},
        'knowledge': {'emoji': '🧠', 'name': 'Знания'},
        'peace': {'emoji': '🌸', 'name': 'Покой'},
        'adrenaline': {'emoji': '⚡', 'name': 'Адреналин'},
        'inspiration': {'emoji': '✨', 'name': 'Вдохновение'}
    }

    moods = {}
    for key, info in moods_data.items():
        videos = Video.query.filter_by(mood=key).order_by(Video.karma.desc()).limit(6).all()
        moods[key] = {
            'emoji': info['emoji'],
            'name': info['name'],
            'videos': videos
        }

    # Чарт — топ 10 по карме
    chart_videos = Video.query.order_by(Video.karma.desc()).limit(10).all()

    # Рекомендации (для залогиненных)
    recommended = []
    if g.user:
        # Берём видео которые пользователь НЕ смотрел
        watched_ids = [h.video_id for h in g.user.watch_history.limit(50).all()]

        if watched_ids:
            recommended = Video.query.filter(
                ~Video.id.in_(watched_ids),
                Video.user_id != g.user.id  # Не свои видео
            ).order_by(Video.karma.desc()).limit(6).all()
        else:
            recommended = Video.query.filter(
                Video.user_id != g.user.id
            ).order_by(Video.karma.desc()).limit(6).all()

    return render_template('index.html',
                           hero_videos=hero_videos,
                           new_videos=new_videos,
                           trending_videos=trending_videos,
                           moods=moods,
                           chart_videos=chart_videos,
                           recommended=recommended
                           )


# ============ СТРАНИЦА НАСТРОЕНИЯ ============

@main_bp.route('/mood/<mood_name>')
def mood(mood_name):
    """Все видео по настроению"""

    valid_moods = {
        'laugh': {'emoji': '😂', 'name': 'Смех'},
        'knowledge': {'emoji': '🧠', 'name': 'Знания'},
        'peace': {'emoji': '🌸', 'name': 'Покой'},
        'adrenaline': {'emoji': '⚡', 'name': 'Адреналин'},
        'inspiration': {'emoji': '✨', 'name': 'Вдохновение'}
    }

    if mood_name not in valid_moods:
        return render_template('errors/404.html'), 404

    mood_info = valid_moods[mood_name]
    videos = Video.query.filter_by(mood=mood_name).order_by(Video.created_at.desc()).all()

    return render_template('mood.html',
                           mood_key=mood_name,
                           mood_info=mood_info,
                           videos=videos
                           )


@main_bp.route('/terms')
def terms():
    """Пользовательское соглашение"""
    return render_template('legal/terms.html')


@main_bp.route('/privacy')
def privacy():
    """Политика конфиденциальности"""
    return render_template('legal/privacy.html')