# app/utils/video_converter.py

import os
import subprocess
import json
from flask import current_app


def get_ffmpeg_path():
    """Возвращает путь к ffmpeg.exe (портативный или системный)"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    portable = os.path.join(project_root, 'ffmpeg', 'ffmpeg.exe')
    if os.path.exists(portable):
        return portable
    return 'ffmpeg'


def get_ffprobe_path():
    """Возвращает путь к ffprobe.exe"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    portable = os.path.join(project_root, 'ffmpeg', 'ffprobe.exe')
    if os.path.exists(portable):
        return portable
    return 'ffprobe'


FFMPEG = get_ffmpeg_path()
FFPROBE = get_ffprobe_path()


def get_video_info(input_path):
    """
    Получает информацию о видео через ffprobe.
    Возвращает (width, height, duration, has_audio)
    """
    try:
        cmd = [
            FFPROBE,
            '-v', 'error',
            '-show_streams',
            '-show_format',
            '-of', 'json',
            input_path
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)
        streams = data.get('streams', [])
        fmt = data.get('format', {})

        width = None
        height = None
        has_audio = False

        for stream in streams:
            if stream.get('codec_type') == 'video' and width is None:
                width = int(stream.get('width', 0))
                height = int(stream.get('height', 0))

            if stream.get('codec_type') == 'audio':
                has_audio = True

        duration = float(fmt.get('duration', 0))

        print(f"📹 ffprobe: {width}x{height}, {duration:.1f}s, аудио={'✅' if has_audio else '❌'}")

        return width, height, duration, has_audio

    except Exception as e:
        print(f"❌ ffprobe ошибка: {e}")
        return None, None, None, False


def convert_to_quality(input_path, output_path, target_height, crf=23):
    """
    Конвертирует видео в нужное качество через subprocess.
    Аудио всегда сохраняется если есть.

    Returns:
        bool: True если успешно
    """
    try:
        width, height, duration, has_audio = get_video_info(input_path)

        if not width or not height:
            print(f"❌ Не удалось получить данные видео: {input_path}")
            return False

        # Считаем новый размер
        if height > target_height:
            new_height = target_height
            new_width = int(width * (target_height / height))
            # Делаем чётными (требование H.264)
            new_width = new_width + (new_width % 2)
            new_height = new_height + (new_height % 2)
        else:
            # Оригинал меньше — оставляем как есть, делаем чётными
            new_width = width + (width % 2)
            new_height = height + (height % 2)

        print(f"⚙️  {target_height}p: {width}x{height} → {new_width}x{new_height}, аудио={'да' if has_audio else 'нет'}")

        # Строим команду
        cmd = [
            FFMPEG,
            '-y',                          # перезаписать если есть
            '-i', input_path,              # входной файл

            # Видео
            '-map', '0:v:0',               # берём первый видеопоток
            '-vf', f'scale={new_width}:{new_height}',  # масштаб
            '-c:v', 'libx264',             # кодек
            '-preset', 'medium',           # скорость/качество
            '-crf', str(crf),              # качество
            '-profile:v', 'high',          # профиль H.264
            '-level', '4.0',
        ]

        # Аудио — если есть
        if has_audio:
            cmd += [
                '-map', '0:a:0',           # берём первый аудиопоток
                '-c:a', 'aac',             # кодек AAC
                '-b:a', '192k',            # битрейт
                '-ac', '2',                # стерео
                '-ar', '48000',            # частота дискретизации
            ]
        else:
            # Нет аудио — явно говорим ffmpeg не трогать аудио
            cmd += ['-an']

        cmd += [
            '-movflags', '+faststart',     # для стриминга
            output_path
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ FFmpeg ошибка при конвертации {target_height}p:")
            print(result.stderr[-1000:] if result.stderr else "нет вывода")
            return False

        if not os.path.exists(output_path):
            print(f"❌ Файл не создан: {output_path}")
            return False

        size_mb = os.path.getsize(output_path) / (1024 * 1024)

        # Проверяем что в результате есть аудио если было в оригинале
        if has_audio:
            _, _, _, result_has_audio = get_video_info(output_path)
            if not result_has_audio:
                print(f"⚠️  Предупреждение: аудио потеряно в {target_height}p!")
            else:
                print(f"✅ {target_height}p готово: {size_mb:.1f} MB (аудио сохранено)")
        else:
            print(f"✅ {target_height}p готово: {size_mb:.1f} MB (без аудио)")

        return True

    except Exception as e:
        print(f"❌ Ошибка конвертации {target_height}p: {e}")
        return False


def convert_video_all_qualities(input_path, base_filename, videos_folder):
    """
    Конвертирует видео во все доступные качества.

    Returns:
        dict: {'1080p': 'filename_1080p.mp4', '720p': 'filename_720p.mp4', ...}
    """
    width, height, duration, has_audio = get_video_info(input_path)

    if not height:
        print("❌ Не удалось получить информацию о видео")
        return {}

    print(f"\n{'='*50}")
    print(f"🎬 Начало конвертации")
    print(f"   Размер: {width}x{height}")
    print(f"   Длина: {duration:.1f} сек")
    print(f"   Аудио: {'есть' if has_audio else 'НЕТ'}")
    print(f"{'='*50}")

    # Определяем какие качества нужны
    if height >= 1080:
        qualities = [
            (1080, 23),
            (720,  24),
            (480,  26),
        ]
    elif height >= 720:
        qualities = [
            (720, 23),
            (480, 25),
        ]
    elif height >= 480:
        qualities = [
            (480, 23),
        ]
    elif height >= 360:
        qualities = [
            (360, 23),
        ]
    else:
        qualities = [
            (240, 23),
        ]

    available = {}

    for target_height, crf in qualities:
        filename = f'{base_filename}_{target_height}p.mp4'
        output_path = os.path.join(videos_folder, filename)

        success = convert_to_quality(
            input_path=input_path,
            output_path=output_path,
            target_height=target_height,
            crf=crf
        )

        if success:
            available[f'{target_height}p'] = filename
        else:
            print(f"⚠️  Качество {target_height}p пропущено")

    print(f"\n{'='*50}")
    print(f"✅ Конвертация завершена: {list(available.keys())}")
    print(f"{'='*50}\n")

    return available


def convert_video(input_path, output_path, max_resolution=1080, crf=23):
    """
    Конвертирует видео в одно качество (обратная совместимость).
    """
    return convert_to_quality(
        input_path=input_path,
        output_path=output_path,
        target_height=max_resolution,
        crf=crf
    )


def get_video_duration(video_path):
    """Получает длительность видео в секундах"""
    try:
        _, _, duration, _ = get_video_info(video_path)
        return duration
    except Exception:
        return None


def get_video_resolution(video_path):
    """Получает разрешение видео"""
    try:
        width, height, _, _ = get_video_info(video_path)
        return width, height
    except Exception:
        return None