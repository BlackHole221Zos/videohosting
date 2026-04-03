# app/routes/video.py

from flask import Blueprint, render_template, redirect, url_for, flash, g, request, abort
from app.extensions import db
from app.models import Video, Comment, Reaction, WatchHistory
from app.forms import VideoUploadForm, CommentForm
from app.utils.decorators import login_required
from app.utils.helpers import save_video, generate_thumbnail

video_bp = Blueprint('video', __name__)


# ============ ЗАГРУЗКА ВИДЕО ============

@video_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Страница загрузки видео"""

    form = VideoUploadForm()

    if form.validate_on_submit():
        # Сохраняем видео файл
        video_filename = save_video(form.video.data)

        if not video_filename:
            flash('Ошибка загрузки видео', 'danger')
            return render_template('video/upload.html', form=form)

        # Генерируем превью
        thumbnail_filename = generate_thumbnail(video_filename)

        # Создаём запись в БД
        video = Video(
            title=form.title.data,
            description=form.description.data or '',
            filename=video_filename,
            thumbnail=thumbnail_filename,
            mood=form.mood.data,
            tags=form.tags.data or '',
            user_id=g.user.id
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

    # Увеличиваем счётчик просмотров
    video.views += 1

    # Записываем в историю (если залогинен)
    if g.user:
        # Проверяем, нет ли уже записи за последний час
        existing = WatchHistory.query.filter_by(
            user_id=g.user.id,
            video_id=video.id
        ).first()

        if not existing:
            history = WatchHistory(user_id=g.user.id, video_id=video.id)
            db.session.add(history)

    db.session.commit()

    # Обработка комментария
    if form.validate_on_submit() and g.user:
        comment = Comment(
            text=form.text.data,
            user_id=g.user.id,
            video_id=video.id
        )
        db.session.add(comment)
        db.session.commit()

        flash('Комментарий добавлен!', 'success')
        return redirect(url_for('video.watch', video_id=video.id))

    # Получаем комментарии
    comments = Comment.query.filter_by(video_id=video.id).order_by(Comment.created_at.desc()).all()

    # Текущая реакция пользователя
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

    return render_template('video/watch.html',
                           video=video,
                           form=form,
                           comments=comments,
                           user_reaction=user_reaction,
                           reactions_count=reactions_count
                           )


# ============ РЕАКЦИЯ НА ВИДЕО ============

@video_bp.route('/video/<int:video_id>/react/<reaction_type>', methods=['POST'])
@login_required
def react(video_id, reaction_type):
    """Добавить/изменить реакцию на видео"""

    if reaction_type not in ['fire', 'good', 'bad']:
        abort(400)

    video = Video.query.get_or_404(video_id)

    # Ищем существующую реакцию
    existing = Reaction.query.filter_by(
        user_id=g.user.id,
        video_id=video.id
    ).first()

    if existing:
        if existing.reaction_type == reaction_type:
            # Убираем реакцию (клик по той же кнопке)
            db.session.delete(existing)
        else:
            # Меняем тип реакции
            existing.reaction_type = reaction_type
    else:
        # Новая реакция
        reaction = Reaction(
            reaction_type=reaction_type,
            user_id=g.user.id,
            video_id=video.id
        )
        db.session.add(reaction)

    # Пересчитываем карму
    db.session.commit()
    video.recalculate_karma()
    db.session.commit()

    return redirect(url_for('video.watch', video_id=video.id))


# ============ УДАЛЕНИЕ ВИДЕО ============

@video_bp.route('/video/<int:video_id>/delete', methods=['POST'])
@login_required
def delete(video_id):
    """Удаление видео (только автор или админ)"""

    video = Video.query.get_or_404(video_id)

    # Проверка прав
    if video.user_id != g.user.id and not g.user.is_admin():
        flash('У вас нет прав на удаление этого видео', 'danger')
        abort(403)

    # Удаляем файлы
    from app.utils.helpers import delete_file
    delete_file(video.filename, 'videos')
    delete_file(video.thumbnail, 'thumbnails')

    # Удаляем из БД
    db.session.delete(video)
    db.session.commit()

    flash('Видео удалено', 'info')
    return redirect(url_for('main.index'))