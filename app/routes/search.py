# app/routes/search.py

from flask import Blueprint, render_template, request
from app.models import Video, User
from sqlalchemy import or_

search_bp = Blueprint('search', __name__)


@search_bp.route('/search')
def search():
    """Поиск видео"""

    query = request.args.get('q', '').strip()
    mood_filter = request.args.get('mood', '')
    sort_by = request.args.get('sort', 'date')

    # Если пустой запрос — показываем пустую страницу
    if not query and not mood_filter:
        return render_template('search/results.html',
                               videos=[],
                               query='',
                               mood_filter='',
                               sort_by=sort_by,
                               total=0
                               )

    # Базовый запрос
    videos_query = Video.query

    # Поиск по тексту
    if query:
        search_pattern = f'%{query}%'
        videos_query = videos_query.filter(
            or_(
                Video.title.ilike(search_pattern),
                Video.description.ilike(search_pattern),
                Video.tags.ilike(search_pattern)
            )
        )

    # Фильтр по настроению
    if mood_filter:
        videos_query = videos_query.filter(Video.mood == mood_filter)

    # Сортировка
    if sort_by == 'views':
        videos_query = videos_query.order_by(Video.views.desc())
    elif sort_by == 'karma':
        videos_query = videos_query.order_by(Video.karma.desc())
    else:  # date
        videos_query = videos_query.order_by(Video.created_at.desc())

    videos = videos_query.all()

    return render_template('search/results.html',
                           videos=videos,
                           query=query,
                           mood_filter=mood_filter,
                           sort_by=sort_by,
                           total=len(videos)
                           )