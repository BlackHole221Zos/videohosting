 🎬 Lampix

Видеохостинг на Flask с системой настроений (Mood), кармой вместо лайков и терминальным дизайном в стиле Gruvbox.

 Возможности

 Видео
- Загрузка MP4, AVI, MOV, MKV, WebM
- Автоконвертация в MP4 (H.264 + AAC) через FFmpeg
- Автогенерация превью из первого кадра
- Кастомный плеер (PiP, широкий режим, скорость, горячие клавиши)
- Система настроений Mood (Смех 😂, Знания 🧠, Покой 🌸, Адреналин ⚡, Вдохновение ✨)
- Карма вместо лайков (🔥 +3, 👍 +1, 👎 -1)
- Комментарии (AJAX)
- История просмотров с группировкой по дням

 Пользователи
- Регистрация и вход
- Восстановление пароля через email
- Профиль (аватар, био, статистика)
- Подписки (карусель аватарок)
- Роли: user, moderator, admin

 Поиск
- По названию, тегам, авторам
- Фильтры по настроению и сортировке

 Прочее
- Тёмная и светлая тема (Gruvbox)
- Toast уведомления
- Юридические документы (PDF)
- Адаптивный дизайн

 Установка

1. Клонируй репозиторий
```bash
git clone https://github.com/BlackHole221Zos/videohosting.git
cd videohosting
```

2. Создай виртуальное окружение
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Установи зависимости
```bash
pip install -r requirements.txt
```

4. Установи FFmpeg
```bash
 Скачай: https://www.gyan.dev/ffmpeg/builds/
 Распакуй в C:\ffmpeg\
 Добавь в PATH: C:\ffmpeg\ffmpeg-8.1-essentials_build\bin
```

5. Создай `.env`
```
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
SECRET_KEY=your-secret-key
```

6. Запусти
```bash
python run.py
```


 Структура проекта
```
videohosting/
├── app/
│   ├── routes/           auth, video, user, search
│   ├── templates/        HTML шаблоны
│   ├── static/           CSS, JS, img
│   ├── utils/            helpers, converter, pdf
│   ├── models.py
│   └── forms.py
├── ffmpeg/               Портативный FFmpeg
├── instance/             База данных SQLite
├── run.py
├── config.py
└── requirements.txt
```

 Зависимости
```
Flask==3.1.3
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.2
Flask-Mail==0.10.0
opencv-python==4.13.0.92
ffmpeg-python==0.2.0
xhtml2pdf==0.2.16
python-dotenv==1.2.2
```

 Планы
- [ ] Админ-панель
- [ ] Уведомления
- [ ] Редактирование видео
- [ ] Плейлисты
- [ ] Творческая студия
- [ ] Выбор качества видео

 Контакты
GitHub: [BlackHole221Zos](https://github.com/BlackHole221Zos)
Email: deniszosimov4@gmail.com

---
