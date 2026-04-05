# app/routes/main.py

from flask import Blueprint, render_template, g, send_from_directory, current_app, abort
from app.models import Video, WatchHistory
import os

main_bp = Blueprint('main', __name__)


# ============ СКАЧАТЬ PDF ============

@main_bp.route('/download/<doc_name>')
def download_pdf(doc_name):
    """Скачать PDF документ"""

    allowed = {'terms.pdf', 'privacy.pdf'}

    if doc_name not in allowed:
        abort(404)

    docs_folder = os.path.join(current_app.static_folder, 'docs')
    filepath = os.path.join(docs_folder, doc_name)

    # Если файл не существует — генерируем
    if not os.path.exists(filepath):
        try:
            from app.utils.pdf_generator import generate_legal_pdfs
            generate_legal_pdfs()
        except Exception as e:
            print(f'Ошибка генерации PDF: {e}')
            abort(404)

    # Проверяем ещё раз
    if not os.path.exists(filepath):
        abort(404)

    return send_from_directory(
        docs_folder,
        doc_name,
        as_attachment=True,
        download_name=doc_name
    )


# ============ ГЛАВНАЯ СТРАНИЦА ============

@main_bp.route('/')
def index():
    """Главная страница"""

    hero_videos = Video.query.filter_by(visibility='public') \
        .order_by(Video.karma.desc()).limit(5).all()

    new_videos = Video.query.filter_by(visibility='public') \
        .order_by(Video.created_at.desc()).limit(12).all()

    all_public = Video.query.filter_by(visibility='public').all()
    trending_videos = sorted(all_public, key=lambda v: v.hot_score(), reverse=True)[:12]

    moods_data = {
        'laugh': {'emoji': '😂', 'name': 'Смех'},
        'knowledge': {'emoji': '🧠', 'name': 'Знания'},
        'peace': {'emoji': '🌸', 'name': 'Покой'},
        'adrenaline': {'emoji': '⚡', 'name': 'Адреналин'},
        'inspiration': {'emoji': '✨', 'name': 'Вдохновение'}
    }

    moods = {}
    for key, info in moods_data.items():
        videos = Video.query.filter_by(mood=key, visibility='public') \
            .order_by(Video.karma.desc()).limit(6).all()
        moods[key] = {
            'emoji': info['emoji'],
            'name': info['name'],
            'videos': videos
        }

    chart_videos = Video.query.filter_by(visibility='public') \
        .order_by(Video.karma.desc()).limit(10).all()

    recommended = []
    if g.user:
        watched_ids = [h.video_id for h in g.user.watch_history.limit(50).all()]

        if watched_ids:
            recommended = Video.query.filter(
                ~Video.id.in_(watched_ids),
                Video.user_id != g.user.id,
                Video.visibility == 'public'
            ).order_by(Video.karma.desc()).limit(6).all()
        else:
            recommended = Video.query.filter(
                Video.user_id != g.user.id,
                Video.visibility == 'public'
            ).order_by(Video.karma.desc()).limit(6).all()

    return render_template('index.html',
                           hero_videos=hero_videos,
                           new_videos=new_videos,
                           trending_videos=trending_videos,
                           moods=moods,
                           chart_videos=chart_videos,
                           recommended=recommended)


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
    videos = Video.query.filter_by(mood=mood_name, visibility='public') \
        .order_by(Video.created_at.desc()).all()

    return render_template('mood.html',
                           mood_key=mood_name,
                           mood_info=mood_info,
                           videos=videos)


@main_bp.route('/terms')
def terms():
    return render_template('legal/terms.html')


@main_bp.route('/privacy')
def privacy():
    return render_template('legal/privacy.html')