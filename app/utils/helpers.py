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
    Сохраняет видео с конвертацией в MP4 (H.264)

    Args:
        video_file: файл из формы (FileStorage)

    Returns:
        str: имя сохранённого файла или None
    """
    if not video_file:
        return None

    # Генерируем уникальное имя
    random_hex = secrets.token_hex(16)
    _, file_ext = os.path.splitext(video_file.filename)

    # Временное имя для оригинала
    temp_filename = f'temp_{random_hex}{file_ext}'
    temp_filepath = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'videos',
        temp_filename
    )

    # Итоговое имя (всегда .mp4)
    final_filename = f'{random_hex}.mp4'
    final_filepath = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'videos',
        final_filename
    )

    try:
        # Сохраняем оригинал временно
        video_file.save(temp_filepath)

        # Конвертируем в MP4 (H.264)
        current_app.logger.info(f'Converting video: {temp_filename} -> {final_filename}')

        success = convert_video(
            input_path=temp_filepath,
            output_path=final_filepath,
            max_resolution=1080,  # Сжимаем до 1080p
            crf=23  # Качество (18-28)
        )

        if not success:
            # Если конвертация не удалась — используем оригинал
            current_app.logger.warning('Conversion failed, using original file')
            os.rename(temp_filepath, final_filepath)
        else:
            # Удаляем временный файл
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)

        return final_filename

    except Exception as e:
        current_app.logger.error(f'Error saving video: {str(e)}')

        # Удаляем временные файлы при ошибке
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        if os.path.exists(final_filepath):
            os.remove(final_filepath)

        return None


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