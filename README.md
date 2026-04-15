```markdown
# 🎬 Lampix — Видеохостинг

> Платформа для загрузки и просмотра видео в терминальном стиле с уникальной системой настроений и кармы.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.1.3-black?style=flat-square)
![FFmpeg](https://img.shields.io/badge/FFmpeg-8.1-green?style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-3-blue?style=flat-square)

## Что это такое?

Lampix — это видеохостинг похожий на YouTube, но с несколькими отличиями:

- Вместо категорий — **настроения (Mood)**. Ты выбираешь под какое настроение твоё видео: Смех 😂, Знания 🧠, Покой 🌸, Адреналин ⚡ или Вдохновение ✨
- Вместо лайков — **карма**. Зрители ставят 🔥 Огонь (+3), 👍 Норм (+1) или 👎 Слабо (-1)
- Дизайн в **терминальном стиле** с CRT-эффектами и цветовой схемой Gruvbox

## Возможности

### Для зрителей
- Смотреть видео через кастомный плеер (широкий режим, PiP, горячие клавиши)
- Оценивать видео через систему кармы
- Оставлять комментарии
- Подписываться на авторов
- Искать видео по названию, тегам, авторам
- История просмотров с группировкой по дням

### Для авторов
- Загружать видео любого формата (MP4, AVI, MOV, MKV, WebM)
- Видео автоматически конвертируется в MP4 (H.264) и сжимается
- Выбирать настроение и теги для видео
- Смотреть статистику (просмотры, карма, подписчики)

### Для администраторов
- Роли пользователей (user, moderator, admin)
- Удаление видео и управление контентом

## Технологии

| Часть | Технологии |
|-------|-----------|
| Backend | Python, Flask, SQLAlchemy, SQLite |
| Авторизация | Кастомная (session, без сторонних библиотек) |
| Видео | FFmpeg 8.1 (конвертация), OpenCV (превью) |
| Frontend | HTML, CSS, Vanilla JavaScript, Fetch API |
| Email | Flask-Mail, Gmail SMTP |
| Формы | Flask-WTF, WTForms |
| PDF | xhtml2pdf |

## Установка и запуск

### Требования
- Python 3.9+
- FFmpeg 8.1

### 1. Клонируй репозиторий

```bash
git clone https://github.com/BlackHole221Zos/videohosting.git
cd videohosting
```

### 2. Создай виртуальное окружение

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. Установи зависимости

```bash
pip install -r requirements.txt
```

### 4. Установи FFmpeg

**Windows:**
- Скачай [ffmpeg-8.1-essentials](https://www.gyan.dev/ffmpeg/builds/)
- Распакуй в C:\ffmpeg\
- Добавь в PATH

**Linux:**

```bash
sudo apt install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

### 5. Создай файл .env

```
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
SECRET_KEY=your-secret-key
```

### 6. Запусти

```bash
python run.py
```

Открой в браузере: **http://127.0.0.1:5000**

### Данные для входа

| Поле | Значение |
|------|----------|
| Логин | admin |
| Пароль | Admin123 |

> Смените пароль после первого входа!

## Структура проекта

```
videohosting/
├── app/
│   ├── routes/          # Маршруты (auth, video, user, search)
│   ├── templates/       # HTML шаблоны (Jinja2)
│   ├── static/          # CSS, JS, изображения
│   ├── utils/           # Вспомогательные функции
│   ├── models.py        # Модели базы данных
│   └── forms.py         # Формы
├── instance/            # База данных SQLite
├── ffmpeg/              # Портативный FFmpeg
├── run.py               # Точка входа
├── config.py            # Конфигурация
└── requirements.txt     # Зависимости
```

## Как это работает

1. Пользователь загружает видео любого формата
2. Сервер конвертирует его в MP4 (H.264 + AAC) через FFmpeg
3. Видео сжимается до 1080p и оптимизируется для стриминга
4. Генерируется превью из первого кадра (OpenCV)
5. Видео доступно для просмотра через кастомный плеер

## Планы на будущее

- [ ] Админ-панель
- [ ] Уведомления
- [ ] Редактирование видео
- [ ] Плейлисты
- [ ] Творческая студия для авторов
- [ ] Выбор качества при просмотре

## Контакты

**GitHub:** [BlackHole221Zos](https://github.com/BlackHole221Zos)

**Email:** deniszosimov4@gmail.com
```
