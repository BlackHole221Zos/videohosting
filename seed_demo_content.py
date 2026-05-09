# seed_demo_content.py
import os
import sys
import json
import random
import secrets
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models import (
    User, Video, Comment, CommentReply, CommentReaction,
    Reaction, WatchHistory
)
from app.utils.video_converter import convert_video_all_qualities
from app.utils.helpers import generate_thumbnail


PROJECT_ROOT = os.path.dirname(__file__)
DEMO_FOLDER = os.path.join(PROJECT_ROOT, "demo_videos")


USERS_DATA = [
    {
        "username": "forest_wave",
        "email": "forest_wave@example.com",
        "bio": "Люблю спокойные видео природы и атмосферные подборки.",
        "role": "user"
    },
    {
        "username": "pixel_ghost",
        "email": "pixel_ghost@example.com",
        "bio": "Публикую короткие атмосферные ролики и визуальные зарисовки.",
        "role": "user"
    },
    {
        "username": "dark_coder",
        "email": "dark_coder@example.com",
        "bio": "Технологии, эстетика, знания и немного спокойствия.",
        "role": "user"
    },
    {
        "username": "calm_horizon",
        "email": "calm_horizon@example.com",
        "bio": "Контент для расслабления, природы и отдыха.",
        "role": "user"
    },
    {
        "username": "ocean_echo",
        "email": "ocean_echo@example.com",
        "bio": "Море, глубина, плавные кадры и красивое настроение.",
        "role": "user"
    },
    {
        "username": "sky_traveler",
        "email": "sky_traveler@example.com",
        "bio": "Путешествия, виды сверху и вдохновляющие ролики.",
        "role": "user"
    },
]


VIDEO_PRESETS = [
    {
        "title": "Тихое утро у реки",
        "description": "Короткое спокойное видео с природной атмосферой и мягким ритмом.",
        "mood": "peace",
        "tags": "природа, река, утро, тишина, покой"
    },
    {
        "title": "Краски природы за одну минуту",
        "description": "Небольшая подборка красивых природных сцен для отдыха и вдохновения.",
        "mood": "inspiration",
        "tags": "природа, красота, вдохновение, пейзаж, атмосфера"
    },
    {
        "title": "Мир природы, который успокаивает",
        "description": "Видео для тех, кто хочет замедлиться, выдохнуть и немного отдохнуть.",
        "mood": "peace",
        "tags": "релакс, природа, спокойствие, отдых, антистресс"
    },
    {
        "title": "Короткий атмосферный пейзаж",
        "description": "Мягкий визуальный ролик с природным настроением и приятной картинкой.",
        "mood": "inspiration",
        "tags": "пейзаж, природа, визуал, красиво, настроение"
    },
    {
        "title": "Природная минутка тишины",
        "description": "Небольшое видео для расслабления и перезагрузки после дня.",
        "mood": "peace",
        "tags": "тишина, природа, расслабление, лес, отдых"
    },
    {
        "title": "Горы и воздух свободы",
        "description": "Короткий вдохновляющий ролик с ощущением простора и высоты.",
        "mood": "inspiration",
        "tags": "горы, свобода, воздух, путешествие, вдохновение"
    },
    {
        "title": "Океаническое спокойствие",
        "description": "Плавное видео с водной атмосферой, мягкими движениями и красивым настроением.",
        "mood": "peace",
        "tags": "океан, море, вода, волны, спокойствие"
    },
    {
        "title": "Природа без спешки",
        "description": "Видео, которое можно просто включить и ненадолго отключиться от суеты.",
        "mood": "peace",
        "tags": "природа, отдых, фон, тишина, медленно"
    },
    {
        "title": "Кадры, которые вдохновляют",
        "description": "Визуальная подборка красивых сцен для лёгкого вдохновения.",
        "mood": "inspiration",
        "tags": "кадры, вдохновение, мир, красиво, визуал"
    },
    {
        "title": "Минутное путешествие по природе",
        "description": "Быстрый взгляд на красивые места, чтобы сменить фокус и немного выдохнуть.",
        "mood": "inspiration",
        "tags": "путешествие, природа, красивые места, короткое видео"
    },
    {
        "title": "Шум воды и мягкий свет",
        "description": "Короткое видео с водой, светом и природной глубиной.",
        "mood": "peace",
        "tags": "вода, свет, медитация, спокойствие, релакс"
    },
    {
        "title": "Природа как антистресс",
        "description": "Небольшой ролик для короткой визуальной паузы и внутреннего выдоха.",
        "mood": "peace",
        "tags": "антистресс, природа, отдых, расслабление, покой"
    },
    {
        "title": "Красивые места в коротком формате",
        "description": "Короткий ролик с атмосферой путешествия и природной эстетикой.",
        "mood": "inspiration",
        "tags": "путешествие, эстетика, природа, короткий ролик"
    },
    {
        "title": "Неспешный взгляд на мир природы",
        "description": "Небольшое видео для спокойного просмотра без перегруза.",
        "mood": "peace",
        "tags": "мир, природа, спокойный просмотр, видео"
    },
    {
        "title": "Энергия дороги и пространства",
        "description": "Ролик с ощущением движения, воздуха и открытого мира.",
        "mood": "adrenaline",
        "tags": "дорога, простор, движение, энергия, путешествие"
    },
]


COMMENT_TEXTS = [
    "Очень атмосферно получилось.",
    "Хороший ролик, приятно смотрится.",
    "Вот это прямо зашло, спокойно и красиво.",
    "Нравится цвет и настроение видео.",
    "Сохранил себе для вечернего просмотра.",
    "Очень приятная подача.",
    "Поймал вайб с первых секунд.",
    "Это как мини-перезагрузка.",
    "Красивый ролик, люблю такое.",
    "Супер, хочется ещё подобного контента.",
    "Вот такие видео реально расслабляют.",
    "Хорошая работа, очень мягкая атмосфера.",
]

REPLY_TEXTS = [
    "Согласен, очень мягкая атмосфера.",
    "Да, тоже это почувствовал.",
    "Точно, тут настроение главное.",
    "Спасибо, рад что зашло.",
    "Тоже люблю такой формат.",
    "Есть в этом что-то очень спокойное.",
    "Вот именно, хорошо расслабляет.",
    "Поддерживаю, отличный визуал.",
    "Да, тут картинка очень приятная.",
    "Согласен, хочется больше такого контента.",
]


def get_demo_files():
    if not os.path.exists(DEMO_FOLDER):
        print(f"❌ Папка demo_videos не найдена: {DEMO_FOLDER}")
        return []

    files = []
    for name in os.listdir(DEMO_FOLDER):
        lower = name.lower()
        if lower.endswith(".mp4") and not lower.endswith(".mp4.part"):
            files.append(os.path.join(DEMO_FOLDER, name))

    return sorted(files)


def create_users():
    users = []

    for data in USERS_DATA:
        user = User.query.filter_by(username=data["username"]).first()
        if not user:
            user = User(
                username=data["username"],
                email=data["email"],
                bio=data["bio"],
                role=data["role"]
            )
            user.set_password("Demo123")
            db.session.add(user)
            db.session.flush()

        users.append(user)

    db.session.commit()
    return users


def create_subscriptions(users):
    for user in users:
        others = [u for u in users if u.id != user.id]
        random.shuffle(others)

        for target in others[:random.randint(1, min(3, len(others)))]:
            if not user.is_following(target):
                user.follow(target)

    db.session.commit()


def unique_title(base_title):
    existing = Video.query.filter_by(title=base_title).first()
    if not existing:
        return base_title

    i = 2
    while True:
        candidate = f"{base_title} #{i}"
        if not Video.query.filter_by(title=candidate).first():
            return candidate
        i += 1


def import_video(source_path, preset, author, upload_folder):
    videos_folder = os.path.join(upload_folder, "videos")

    base_name = secrets.token_hex(16)

    print(f"\n🎬 Импорт файла: {os.path.basename(source_path)}")
    print(f"   Автор: {author.username}")
    print(f"   Название: {preset['title']}")

    qualities = convert_video_all_qualities(
        input_path=source_path,
        base_filename=base_name,
        videos_folder=videos_folder
    )

    if not qualities:
        print("   ❌ Не удалось сконвертировать видео")
        return None

    main_filename = None
    for q in ['1080p', '720p', '480p', '360p', '240p']:
        if q in qualities:
            main_filename = qualities[q]
            break

    if not main_filename:
        main_filename = list(qualities.values())[0]

    thumbnail = generate_thumbnail(main_filename)

    created_at = datetime.utcnow() - timedelta(
        days=random.randint(0, 20),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

    video = Video(
        title=unique_title(preset["title"]),
        description=preset["description"],
        filename=main_filename,
        thumbnail=thumbnail,
        user_id=author.id,
        mood=preset["mood"],
        tags=preset["tags"],
        visibility='public',
        views=random.randint(12, 300),
        karma=0,
        qualities=json.dumps(qualities, ensure_ascii=False),
        created_at=created_at
    )

    db.session.add(video)
    db.session.commit()

    print(f"   ✅ Видео создано: ID={video.id}")
    return video


def add_reactions(video, users):
    shuffled = users[:]
    random.shuffle(shuffled)

    count = random.randint(2, min(5, len(shuffled)))
    used = 0

    for user in shuffled[:count]:
        existing = Reaction.query.filter_by(user_id=user.id, video_id=video.id).first()
        if existing:
            continue

        reaction_type = random.choices(
            population=["fire", "good", "bad"],
            weights=[50, 40, 10],
            k=1
        )[0]

        reaction = Reaction(
            reaction_type=reaction_type,
            user_id=user.id,
            video_id=video.id,
            created_at=video.created_at + timedelta(minutes=random.randint(2, 400))
        )
        db.session.add(reaction)
        used += 1

    db.session.commit()
    video.recalculate_karma()
    db.session.commit()
    return used


def add_comments_and_replies(video, users):
    comments_created = []

    comment_authors = users[:]
    random.shuffle(comment_authors)

    count = random.randint(2, 5)

    for i in range(count):
        author = comment_authors[i % len(comment_authors)]

        comment = Comment(
            text=random.choice(COMMENT_TEXTS),
            user_id=author.id,
            video_id=video.id,
            created_at=video.created_at + timedelta(minutes=random.randint(5, 700))
        )
        db.session.add(comment)
        db.session.flush()
        comments_created.append(comment)

        # Реакции на комментарий
        reactors = users[:]
        random.shuffle(reactors)

        for reactor in reactors[:random.randint(0, 3)]:
            if reactor.id == author.id:
                continue

            exists = CommentReaction.query.filter_by(
                user_id=reactor.id,
                comment_id=comment.id
            ).first()

            if not exists:
                comment_reaction = CommentReaction(
                    reaction_type=random.choices(
                        population=["like", "dislike"],
                        weights=[85, 15],
                        k=1
                    )[0],
                    user_id=reactor.id,
                    comment_id=comment.id,
                    created_at=comment.created_at + timedelta(minutes=random.randint(1, 50))
                )
                db.session.add(comment_reaction)

        # Ответы на комментарий
        reply_users = users[:]
        random.shuffle(reply_users)

        for reply_author in reply_users[:random.randint(0, 2)]:
            reply = CommentReply(
                text=random.choice(REPLY_TEXTS),
                user_id=reply_author.id,
                comment_id=comment.id,
                created_at=comment.created_at + timedelta(minutes=random.randint(1, 120))
            )
            db.session.add(reply)

    db.session.commit()
    return len(comments_created)


def add_watch_history(video, users):
    watchers = users[:]
    random.shuffle(watchers)

    count = 0
    for user in watchers[:random.randint(1, min(5, len(watchers)))]:
        item = WatchHistory(
            user_id=user.id,
            video_id=video.id,
            watched_at=video.created_at + timedelta(minutes=random.randint(3, 1000))
        )
        db.session.add(item)
        count += 1

    db.session.commit()
    return count


def main():
    print("=" * 70)
    print("ЗАПОЛНЕНИЕ LAMPIX ДЕМО-КОНТЕНТОМ")
    print("=" * 70)

    files = get_demo_files()
    if not files:
        print("❌ В папке demo_videos нет готовых .mp4 файлов")
        return

    print(f"Найдено .mp4 файлов: {len(files)}")
    for file_path in files:
        print(f" - {os.path.basename(file_path)}")

    answer = input("\nСоздать демо-контент? (yes/no): ").strip().lower()
    if answer not in ("yes", "y", "да"):
        print("⏭️ Отменено")
        return

    users = create_users()
    create_subscriptions(users)

    print(f"\n✅ Пользователи готовы: {len(users)}")
    print("Пароль для всех демо-пользователей: Demo123")

    upload_folder = app.config['UPLOAD_FOLDER']

    imported = 0

    for i, source_path in enumerate(files):
        preset = VIDEO_PRESETS[i % len(VIDEO_PRESETS)]
        author = random.choice(users)

        video = import_video(source_path, preset, author, upload_folder)
        if not video:
            continue

        reactions_count = add_reactions(video, users)
        comments_count = add_comments_and_replies(video, users)
        history_count = add_watch_history(video, users)

        print(f"   👍 Реакции: {reactions_count}")
        print(f"   💬 Комментарии: {comments_count}")
        print(f"   👁 История просмотров: {history_count}")

        imported += 1

    print("\n" + "=" * 70)
    print("ГОТОВО")
    print("=" * 70)
    print(f"Импортировано видео: {imported}")
    print(f"Пользователей: {len(users)}")
    print("Логины пользователей:")
    for user in users:
        print(f" - {user.username}")
    print("=" * 70)


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        main()