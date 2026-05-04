# app/utils/helpers.py

import os
import secrets
import uuid  # 🆕 ДОБАВИЛ
import cv2
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename
from app.utils.video_converter import convert_video

# ============ РАЗРЕШЁННЫЕ РАСШИРЕНИЯ ============

ALLOWED_VIDEO = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
ALLOWED_IMAGE = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def allowed_file(filename, allowed_extensions):
    """Проверяет разрешено ли расширение файла"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions


def generate_unique_filename(original_filename):
    """Генерирует уникальное имя файла, сохраняя расширение"""
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_name = uuid.uuid4().hex
    return f"{unique_name}.{ext}" if ext else unique_name


# ============ СОХРАНЕНИЕ ВИДЕО ============

def save_video(video_file):
    """
    Сохраняет видео и конвертирует в несколько качеств

    Returns:
        tuple: (основной файл, словарь качеств) или (None, {})
    """
    import json
    from app.utils.video_converter import convert_video_all_qualities

    if not video_file:
        return None, {}

    # Генерируем уникальное базовое имя
    base_name = secrets.token_hex(16)
    _, file_ext = os.path.splitext(video_file.filename)

    videos_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos')

    # Временный файл оригинала
    temp_filename = f'temp_{base_name}{file_ext}'
    temp_filepath = os.path.join(videos_folder, temp_filename)

    try:
        # Сохраняем оригинал
        video_file.save(temp_filepath)
        original_size = os.path.getsize(temp_filepath) / (1024 * 1024)
        current_app.logger.info(f'📁 Оригинал: {temp_filename} ({original_size:.1f} MB)')

        # Конвертируем во все качества
        available_qualities = convert_video_all_qualities(
            input_path=temp_filepath,
            base_filename=base_name,
            videos_folder=videos_folder
        )

        # Удаляем временный файл
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)

        if not available_qualities:
            current_app.logger.error('❌ Не удалось сконвертировать ни одного качества')
            return None, {}

        # Основной файл = лучшее доступное качество
        main_filename = None
        for q in ['1080p', '720p', '480p', '360p', '240p']:
            if q in available_qualities:
                main_filename = available_qualities[q]
                break

        # Если ничего не нашли — берём первый доступный
        if not main_filename and available_qualities:
            main_filename = list(available_qualities.values())[0]

        current_app.logger.info(f'✅ Готово: {available_qualities}')
        return main_filename, available_qualities

    except Exception as e:
        current_app.logger.error(f'❌ Ошибка: {str(e)}')
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        return None, {}


# ============ ГЕНЕРАЦИЯ ПРЕВЬЮ ============

def generate_thumbnail(video_filename):
    """
    Генерирует превью из первого кадра видео.
    Возвращает имя файла превью или 'default_thumb.jpg' при ошибке.
    """
    try:
        video_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'videos',
            video_filename
        )

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return 'default_thumb.jpg'

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return 'default_thumb.jpg'

        thumb_filename = f"thumb_{uuid.uuid4().hex}.jpg"
        thumb_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'thumbnails')

        os.makedirs(thumb_folder, exist_ok=True)

        thumb_path = os.path.join(thumb_folder, thumb_filename)

        cv2.imwrite(thumb_path, frame)

        return thumb_filename

    except Exception as e:
        current_app.logger.error(f"Ошибка генерации превью: {e}")
        return 'default_thumb.jpg'


# ============ СОХРАНЕНИЕ ОБЛОЖКИ ============

def save_thumbnail(thumbnail_file):
    """
    Сохраняет пользовательскую обложку видео.
    Возвращает имя файла или None при ошибке.
    """
    if not thumbnail_file:
        return None

    if not allowed_file(thumbnail_file.filename, ALLOWED_IMAGE):
        return None

    filename = generate_unique_filename(thumbnail_file.filename)
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'thumbnails')

    os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, filename)
    thumbnail_file.save(filepath)

    return filename


# ============ СОХРАНЕНИЕ АВАТАРА ============

def save_avatar(avatar_file, username):
    """
    Сохраняет аватар пользователя.
    Возвращает имя файла или None при ошибке.
    """
    if not avatar_file:
        return None

    if not allowed_file(avatar_file.filename, ALLOWED_IMAGE):
        return None

    ext = avatar_file.filename.rsplit('.', 1)[1].lower()
    filename = f"avatar_{secure_filename(username)}_{uuid.uuid4().hex[:8]}.{ext}"

    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
    os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, filename)
    avatar_file.save(filepath)

    return filename


# ============ УДАЛЕНИЕ ФАЙЛОВ ============

def delete_file(filename, folder):
    """
    Удаляет файл из указанной папки.
    folder: 'videos', 'thumbnails', 'avatars'
    """
    if not filename or filename.startswith('default'):
        return False

    try:
        filepath = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            folder,
            filename
        )
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        current_app.logger.error(f"Ошибка удаления файла: {e}")

    return False