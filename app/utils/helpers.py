# app/utils/helpers.py

import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

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
    Сохраняет видео файл.
    Возвращает имя сохранённого файла или None при ошибке.
    """
    if not video_file:
        return None

    if not allowed_file(video_file.filename, ALLOWED_VIDEO):
        return None

    filename = generate_unique_filename(video_file.filename)
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos')

    # Создаём папку если не существует
    os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, filename)
    video_file.save(filepath)

    return filename


# ============ ГЕНЕРАЦИЯ ПРЕВЬЮ ============

def generate_thumbnail(video_filename):
    """
    Генерирует превью из первого кадра видео.
    Возвращает имя файла превью или 'default_thumb.jpg' при ошибке.
    """
    try:
        import cv2

        video_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'videos',
            video_filename
        )

        # Открываем видео
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return 'default_thumb.jpg'

        # Читаем первый кадр
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return 'default_thumb.jpg'

        # Генерируем имя для превью
        thumb_filename = f"thumb_{uuid.uuid4().hex}.jpg"
        thumb_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'thumbnails')

        os.makedirs(thumb_folder, exist_ok=True)

        thumb_path = os.path.join(thumb_folder, thumb_filename)

        # Сохраняем превью
        cv2.imwrite(thumb_path, frame)

        return thumb_filename

    except Exception as e:
        print(f"Ошибка генерации превью: {e}")
        return 'default_thumb.jpg'


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

    # Безопасное имя с привязкой к пользователю
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
        print(f"Ошибка удаления файла: {e}")

    return False