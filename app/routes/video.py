# app/routes/video.py

from flask import Blueprint, render_template, redirect, url_for, flash, g, request, abort, jsonify
from app.extensions import db
from app.models import Video, Comment, Reaction, WatchHistory
from app.forms import VideoUploadForm, CommentForm
from app.utils.decorators import login_required
from app.utils.helpers import save_video, generate_thumbnail, delete_file, save_thumbnail
from datetime import datetime

video_bp = Blueprint('video', __name__)


# ============ ЗАГРУЗКА ВИДЕО ============

@video_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Страница загрузки видео"""
    import json

    form = VideoUploadForm()

    if form.validate_on_submit():
        # Сохраняем видео файл (теперь возвращает кортеж)
        video_filename, qualities = save_video(form.video.data)

        if not video_filename:
            flash('Ошибка загрузки видео', 'danger')
            return render_template('video/upload.html', form=form)

        # Превью: своё или автогенерация
        if form.thumbnail.data:
            thumbnail_filename = save_thumbnail(form.thumbnail.data)
        else:
            thumbnail_filename = generate_thumbnail(video_filename)

        # Создаём запись в БД
        video = Video(
            title=form.title.data,
            description=form.description.data or '',
            filename=video_filename,
            thumbnail=thumbnail_filename,
            mood=form.mood.data,
            visibility=form.visibility.data,
            tags=form.tags.data or '',
            user_id=g.user.id,
            qualities=json.dumps(qualities)
        )

        db.session.add(video)
        db.session.commit()

        flash('Видео успешно загружено!', 'success')
        return redirect(url_for('video.watch', video_id=video.id))

    return render_template('video/upload.html', form=form)


# ============ ПРОСМОТР ВИДЕО ============

@video_bp.route('/video/<int:video_id>', methods=['GET', 'POST'])
def watch(video_id):
    """Страница просмотра видео"""

    video = Video.query.get_or_404(video_id)
    form = CommentForm()

    # Увеличиваем просмотры
    video.views += 1

    # Записываем в историю
    if g.user:
        existing = WatchHistory.query.filter_by(
            user_id=g.user.id,
            video_id=video.id
        ).first()

        if existing:
            # Обновляем время просмотра
            existing.watched_at = datetime.utcnow()
        else:
            history = WatchHistory(user_id=g.user.id, video_id=video.id)
            db.session.add(history)

    db.session.commit()

    comments = Comment.query.filter_by(video_id=video.id) \
        .order_by(Comment.created_at.desc()).all()

    # Реакция пользователя
    user_reaction = None
    if g.user:
        reaction = Reaction.query.filter_by(user_id=g.user.id, video_id=video.id).first()
        if reaction:
            user_reaction = reaction.reaction_type

    # Подсчёт реакций
    reactions_count = {
        'fire': Reaction.query.filter_by(video_id=video.id, reaction_type='fire').count(),
        'good': Reaction.query.filter_by(video_id=video.id, reaction_type='good').count(),
        'bad': Reaction.query.filter_by(video_id=video.id, reaction_type='bad').count()
    }

    # Похожие видео
    related = Video.query.filter(
        Video.id != video.id,
        Video.mood == video.mood
    ).order_by(Video.views.desc()).limit(8).all()

    if len(related) < 4:
        more = Video.query.filter(Video.id != video.id).order_by(Video.karma.desc()).limit(8).all()
        seen_ids = {v.id for v in related}
        for v in more:
            if v.id not in seen_ids:
                related.append(v)
            if len(related) >= 8:
                break

    return render_template('video/watch.html',
                           video=video,
                           form=form,
                           comments=comments,
                           user_reaction=user_reaction,
                           reactions_count=reactions_count,
                           related_videos=related)


# ============ РЕАКЦИЯ НА ВИДЕО (AJAX) ============

@video_bp.route('/video/<int:video_id>/react/<reaction_type>', methods=['POST'])
@login_required
def react(video_id, reaction_type):
    """Добавить/изменить реакцию (AJAX)"""

    if reaction_type not in ['fire', 'good', 'bad']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Invalid reaction'}), 400
        abort(400)

    video = Video.query.get_or_404(video_id)

    # Ищем существующую реакцию
    existing = Reaction.query.filter_by(
        user_id=g.user.id,
        video_id=video.id
    ).first()

    new_reaction = None

    if existing:
        if existing.reaction_type == reaction_type:
            # Убираем реакцию
            db.session.delete(existing)
            new_reaction = None
        else:
            # Меняем тип
            existing.reaction_type = reaction_type
            new_reaction = reaction_type
    else:
        # Новая реакция
        reaction = Reaction(
            reaction_type=reaction_type,
            user_id=g.user.id,
            video_id=video.id
        )
        db.session.add(reaction)
        new_reaction = reaction_type

    db.session.commit()
    video.recalculate_karma()
    db.session.commit()

    # Подсчёт реакций
    reactions_count = {
        'fire': Reaction.query.filter_by(video_id=video.id, reaction_type='fire').count(),
        'good': Reaction.query.filter_by(video_id=video.id, reaction_type='good').count(),
        'bad': Reaction.query.filter_by(video_id=video.id, reaction_type='bad').count()
    }

    # AJAX запрос — возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'user_reaction': new_reaction,
            'reactions': reactions_count,
            'karma': video.karma
        })

    # Обычный запрос — редирект
    return redirect(url_for('video.watch', video_id=video.id))


# ============ ДОБАВИТЬ КОММЕНТАРИЙ (AJAX) ============

@video_bp.route('/video/<int:video_id>/comment', methods=['POST'])
@login_required
def add_comment(video_id):
    """Добавить комментарий (AJAX)"""

    video = Video.query.get_or_404(video_id)

    # AJAX запрос
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        text = request.json.get('text', '').strip()

        if not text:
            return jsonify({'error': 'Комментарий не может быть пустым'}), 400

        if len(text) > 1000:
            return jsonify({'error': 'Комментарий слишком длинный'}), 400

        comment = Comment(
            text=text,
            user_id=g.user.id,
            video_id=video.id
        )
        db.session.add(comment)
        db.session.commit()

        return jsonify({
            'success': True,
            'comment': {
                'id': comment.id,
                'text': comment.text,
                'author': {
                    'username': g.user.username,
                    'avatar': g.user.avatar
                },
                'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M')
            }
        })

    # Обычная форма (fallback)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            text=form.text.data,
            user_id=g.user.id,
            video_id=video.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен!', 'success')

    return redirect(url_for('video.watch', video_id=video.id))


# ============ УДАЛЕНИЕ ВИДЕО ============

@video_bp.route('/video/<int:video_id>/delete', methods=['POST'])
@login_required
def delete(video_id):
    """Удаление видео"""

    video = Video.query.get_or_404(video_id)

    if video.user_id != g.user.id and not g.user.is_admin():
        flash('У вас нет прав на удаление этого видео', 'danger')
        abort(403)

    from app.utils.helpers import delete_file
    delete_file(video.filename, 'videos')
    delete_file(video.thumbnail, 'thumbnails')

    db.session.delete(video)
    db.session.commit()

    flash('Видео удалено', 'info')
    return redirect(url_for('main.index'))

# ============ УДАЛЕНИЕ КОММЕНТАРИЯ (AJAX) ============

@video_bp.route('/video/<int:video_id>/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(video_id, comment_id):
    """Удаление комментария (AJAX)"""

    comment = Comment.query.get_or_404(comment_id)
    video = Video.query.get_or_404(video_id)

    # Проверяем права:
    # - автор комментария
    # - автор видео
    # - модератор или админ
    can_delete = (
        comment.user_id == g.user.id or
        video.user_id == g.user.id or
        g.user.is_moderator()
    )

    if not can_delete:
        return jsonify({'error': 'Нет прав'}), 403

    db.session.delete(comment)
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'comment_id': comment_id})

    flash('Комментарий удалён', 'info')
    return redirect(url_for('video.watch', video_id=video_id))