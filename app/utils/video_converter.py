# app/utils/video_converter.py

import os
import sys
import ffmpeg
from flask import current_app


def get_ffmpeg_path():
    """Возвращает путь к FFmpeg (портативный или системный)"""
    # Проверяем портативную версию в корне проекта
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    portable_ffmpeg = os.path.join(project_root, 'ffmpeg', 'ffmpeg.exe')

    if os.path.exists(portable_ffmpeg):
        return os.path.dirname(portable_ffmpeg)

    # Иначе используем системный FFmpeg
    return None


# Устанавливаем путь к FFmpeg при импорте модуля
ffmpeg_path = get_ffmpeg_path()
if ffmpeg_path:
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")
    print(f"✅ Используется портативный FFmpeg: {ffmpeg_path}")
else:
    print("⚙️ Используется системный FFmpeg")


def convert_video(input_path, output_path, max_resolution=1080, crf=23):
    """
    Конвертирует видео в оптимизированный MP4 (H.264 + AAC)

    Args:
        input_path (str): путь к исходному видео
        output_path (str): путь к выходному видео
        max_resolution (int): максимальная высота (720, 1080, None = оригинал)
        crf (int): качество 18-28 (меньше = лучше, 23 = оптимально)

    Returns:
        bool: True если успешно, False если ошибка
    """
    try:
        # Получаем информацию о видео
        probe = ffmpeg.probe(input_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')

        width = int(video_info['width'])
        height = int(video_info['height'])

        # Создаём input stream
        stream = ffmpeg.input(input_path)

        # Если нужно сжать разрешение
        if max_resolution and height > max_resolution:
            # Сохраняем пропорции
            new_height = max_resolution
            new_width = int(width * (max_resolution / height))

            # Делаем чётными (требование H.264)
            new_width = new_width - (new_width % 2)
            new_height = new_height - (new_height % 2)

            stream = stream.filter('scale', new_width, new_height)

        # Конвертируем
        stream = ffmpeg.output(
            stream,
            output_path,
            vcodec='libx264',  # Видео кодек H.264
            acodec='aac',  # Аудио кодек AAC
            crf=crf,  # Качество (18-28)
            preset='medium',  # Скорость (ultrafast, fast, medium, slow)
            movflags='faststart',  # Оптимизация для веб-стриминга
            **{'c:a': 'aac', 'b:a': '128k'}  # Аудио битрейт
        )

        # Запускаем конвертацию (перезаписываем если существует)
        ffmpeg.run(stream, overwrite_output=True, quiet=True)

        return True

    except ffmpeg.Error as e:
        # Логируем ошибку
        error_message = e.stderr.decode() if e.stderr else str(e)
        current_app.logger.error(f'FFmpeg error: {error_message}')
        return False

    except Exception as e:
        current_app.logger.error(f'Video conversion error: {str(e)}')
        return False


def get_video_duration(video_path):
    """
    Получает длительность видео в секундах

    Args:
        video_path (str): путь к видео

    Returns:
        float: длительность в секундах или None
    """
    try:
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        return duration
    except:
        return None


def get_video_resolution(video_path):
    """
    Получает разрешение видео

    Args:
        video_path (str): путь к видео

    Returns:
        tuple: (width, height) или None
    """
    try:
        probe = ffmpeg.probe(video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        return (width, height)
    except:
        return None