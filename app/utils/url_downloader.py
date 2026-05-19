# app/utils/url_downloader.py
import os
import secrets
import subprocess
import json  # ← ЭТО БЫЛО ПРОПУЩЕНО!
import sys
from flask import current_app
from app.utils.video_converter import convert_video_all_qualities
from app.utils.helpers import generate_thumbnail


def get_yt_dlp_path():
    """Улучшенный поиск yt-dlp"""
    import shutil

    path = shutil.which('yt-dlp')
    if path:
        print(f"✅ yt-dlp найден в PATH: {path}")
        return path

    # Для Windows venv
    if sys.platform == 'win32':
        venv_paths = [
            os.path.join(os.path.dirname(sys.executable), 'Scripts', 'yt-dlp.exe'),
            os.path.join(os.path.dirname(sys.executable), 'yt-dlp.exe'),
        ]
        for p in venv_paths:
            if os.path.exists(p):
                print(f"✅ yt-dlp найден в venv: {p}")
                return p

    print("⚠️ yt-dlp используется из PATH")
    return 'yt-dlp'


def get_video_info_from_url(url):
    """Получить информацию о видео по ссылке"""
    yt_dlp = get_yt_dlp_path()

    cmd = [
        yt_dlp,
        '--dump-json',
        '--no-download',
        '--no-playlist',
        '--ignore-errors',
        url
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=25,
            encoding='utf-8'
        )

        if result.returncode != 0:
            print(f"yt-dlp info error: {result.stderr[-400:]}")
            return None

        data = json.loads(result.stdout.strip())

        return {
            'title': str(data.get('title', 'Без названия'))[:200],
            'description': str(data.get('description', ''))[:2000],
            'duration': data.get('duration', 0),
            'uploader': str(data.get('uploader', '')),
            'thumbnail_url': data.get('thumbnail', ''),
            'extractor': data.get('extractor_key', 'external'),
        }

    except json.JSONDecodeError:
        print("❌ Ошибка: yt-dlp вернул некорректный JSON")
        return None
    except Exception as e:
        print(f"url_downloader get_info error: {e}")
        return None


def download_video_from_url(url):
    """Скачивает видео по URL"""
    yt_dlp = get_yt_dlp_path()
    videos_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos')
    os.makedirs(videos_folder, exist_ok=True)

    base_name = secrets.token_hex(16)
    temp_filename = f'url_temp_{base_name}.mp4'
    temp_path = os.path.join(videos_folder, temp_filename)

    try:
        cmd = [
            yt_dlp,
            '-f', 'b[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            '--no-playlist',
            '--no-part',
            '--merge-output-format', 'mp4',
            '-o', temp_path,
            url
        ]

        print(f"📥 Скачивание видео: {url}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            print(f"yt-dlp download error: {result.stderr[-500:]}")
            return None, {}, None

        if not os.path.exists(temp_path):
            print("❌ Файл не был создан")
            return None, {}, None

        # Конвертируем в несколько качеств
        qualities = convert_video_all_qualities(
            input_path=temp_path,
            base_filename=base_name,
            videos_folder=videos_folder
        )

        if os.path.exists(temp_path):
            os.remove(temp_path)

        if not qualities:
            return None, {}, None

        main_filename = next((qualities[q] for q in ['1080p','720p','480p'] if q in qualities),
                           list(qualities.values())[0])

        thumbnail = generate_thumbnail(main_filename)

        return main_filename, qualities, thumbnail

    except Exception as e:
        print(f"❌ Ошибка в download_video_from_url: {e}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return None, {}, None