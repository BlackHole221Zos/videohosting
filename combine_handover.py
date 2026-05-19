# combine_handover.py
import os
from datetime import datetime

# ================== НАСТРОЙКИ ==================
FILES = [
    ("app/models.py", "MODELS"),
    ("app/routes/video.py", "ROUTES_VIDEO"),
    ("app/forms.py", "FORMS"),
    ("app/templates/video/upload.html", "TEMPLATE_UPLOAD"),
    ("app/utils/url_downloader.py", "UTILS_URL_DOWNLOADER"),
    ("app/utils/video_converter.py", "UTILS_VIDEO_CONVERTER"),
    ("app/utils/helpers.py", "UTILS_HELPERS"),
    ("app/templates/video/watch.html", "TEMPLATE_WATCH"),
    ("app/static/js/main.js", "STATIC_MAIN_JS"),
]

OUTPUT_FILE = "HANDOVER_FULL.txt"


# ===============================================

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"!!! ФАЙЛ НЕ НАЙДЕН: {path}"
    except Exception as e:
        return f"!!! ОШИБКА ЧТЕНИЯ {path}: {e}"


def main():
    print("🚀 Начинаем сборку HANDOVER_FULL.txt...\n")

    content = []
    content.append("=" * 80)
    content.append("🔥 LAMPiX — ПОЛНЫЙ HANDOVER ДЛЯ ИИ")
    content.append(f"Дата сборки: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    content.append("Цель: Добавление импорта видео по внешней ссылке (yt-dlp)")
    content.append("=" * 80)
    content.append("\n")

    for filepath, section_name in FILES:
        print(f"📄 Читаем: {filepath}")
        file_content = read_file(filepath)

        content.append("\n" + "=" * 90)
        content.append(f"📁 ФАЙЛ: {filepath}")
        content.append(f"🔖 СЕКЦИЯ: {section_name}")
        content.append("=" * 90)
        content.append("\n")
        content.append(file_content)
        content.append("\n" + "=" * 90 + "\n")

    # Записываем всё в один файл
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))

    print(f"\n✅ Готово! Файл создан: **{OUTPUT_FILE}**")
    print(f"   Размер: {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")


if __name__ == "__main__":
    main()