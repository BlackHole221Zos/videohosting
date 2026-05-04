# app/utils/video_converter.py

import os
import ffmpeg
from flask import current_app


def get_ffmpeg_path():
    """Возвращает путь к FFmpeg (портативный или системный)"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    portable_ffmpeg = os.path.join(project_root, 'ffmpeg', 'ffmpeg.exe')

    if os.path.exists(portable_ffmpeg):
        return os.path.dirname(portable_ffmpeg)
    return None


# Устанавливаем путь к FFmpeg при импорте модуля
ffmpeg_path = get_ffmpeg_path()
if ffmpeg_path:
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")
    print(f"✅ Используется портативный FFmpeg: {ffmpeg_path}")
else:
    print("⚙️ Используется системный FFmpeg")


def get_video_info(input_path):
    """Получает информацию о видео (ширина, высота, длительность)"""
    try:
        probe = ffmpeg.probe(input_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        duration = float(probe['format']['duration'])
        return width, height, duration
    except Exception as e:
        return None, None, None


def convert_to_quality(input_path, output_path, height, crf=23):
    """
    Конвертирует видео в заданное качество

    Args:
        input_path (str): путь к исходному видео
        output_path (str): путь к выходному видео
        height (int): высота видео (480, 720, 1080)
        crf (int): качество (18-28)

    Returns:
        bool: True если успешно
    """
    try:
        probe = ffmpeg.probe(input_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')

        orig_width = int(video_info['width'])
        orig_height = int(video_info['height'])

        stream = ffmpeg.input(input_path)

        # Масштабируем только если оригинал больше нужного качества
        if orig_height > height:
            new_height = height
            new_width = int(orig_width * (height / orig_height))
            # Делаем чётными (требование H.264)
            new_width = new_width - (new_width % 2)
            new_height = new_height - (new_height % 2)
            stream = stream.filter('scale', new_width, new_height)

        stream = ffmpeg.output(
            stream,
            output_path,
            vcodec='libx264',
            acodec='aac',
            crf=crf,
            preset='medium',
            movflags='faststart',
            **{'b:a': '128k'}
        )

        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        return True

    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if e.stderr else str(e)
        print(f'FFmpeg error: {error_message}')
        return False

    except Exception as e:
        print(f'Video conversion error: {str(e)}')
        return False


def convert_video_all_qualities(input_path, base_filename, videos_folder):
    """
    Конвертирует видео во все доступные качества

    Args:
        input_path (str): путь к исходному видео
        base_filename (str): базовое имя файла (без расширения)
        videos_folder (str): папка для сохранения

    Returns:
        dict: словарь доступных качеств {качество: имя файла}
        Пример: {'1080p': 'abc123_1080p.mp4', '720p': 'abc123_720p.mp4', '480p': 'abc123_480p.mp4'}
    """
    # Получаем информацию о видео
    orig_width, orig_height, duration = get_video_info(input_path)

    if not orig_height:
        print('❌ Не удалось получить информацию о видео')
        return {}

    print(f'📹 Оригинал: {orig_width}x{orig_height}, {duration:.1f} сек')

    qualities = []
    if orig_height >= 1080:
        qualities = [1080, 720, 480]
    elif orig_height >= 720:
        qualities = [720, 480]
    elif orig_height >= 480:
        qualities = [480]
    elif orig_height >= 360:
        qualities = [360]
    elif orig_height >= 240:
        qualities = [240]
    else:
        qualities = [orig_height]

    available = {}

    for q in qualities:
        # CRF зависит от качества
        crf_map = {1080: 23, 720: 24, 480: 26, 360: 27, 240: 28}
        crf = crf_map.get(q, 23)

        filename = f'{base_filename}_{q}p.mp4'
        output_path = os.path.join(videos_folder, filename)

        print(f'⚙️ Конвертация в {q}p (CRF {crf})...')

        success = convert_to_quality(
            input_path=input_path,
            output_path=output_path,
            height=q,
            crf=crf
        )

        if success:
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f'✅ {q}p готово: {filename} ({size_mb:.1f} MB)')
            available[f'{q}p'] = filename
        else:
            print(f'❌ Ошибка конвертации {q}p')

    return available


def convert_video(input_path, output_path, max_resolution=1080, crf=23):
    """
    Конвертирует видео в одно качество (обратная совместимость)
    """
    return convert_to_quality(input_path, output_path, max_resolution, crf)


def get_video_duration(video_path):
    """Получает длительность видео в секундах"""
    try:
        probe = ffmpeg.probe(video_path)
        return float(probe['format']['duration'])
    except:
        return None


def get_video_resolution(video_path):
    """Получает разрешение видео"""
    try:
        probe = ffmpeg.probe(video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        return int(video_info['width']), int(video_info['height'])
    except:
        return None