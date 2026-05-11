# seed_demo_content.py
import os
import sys
import json
import random
import hashlib
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models import (
    User,
    Video,
    Comment,
    CommentReply,
    CommentReaction,
    Reaction,
    WatchHistory,
)
from app.utils.video_converter import convert_video_all_qualities
from app.utils.helpers import generate_thumbnail


PROJECT_ROOT = os.path.dirname(__file__)
DEMO_FOLDER = os.path.join(PROJECT_ROOT, "demo_videos")
IMPORT_STATE_FILE = os.path.join(PROJECT_ROOT, "instance", "seed_demo_imports.json")


USERS_DATA = [
    {
        "username": "forest_wave",
        "email": "forest_wave@example.com",
        "bio": "Люблю спокойные видео природы и атмосферные подборки.",
        "role": "user",
        "moods": ["peace", "inspiration"],
    },
    {
        "username": "pixel_ghost",
        "email": "pixel_ghost@example.com",
        "bio": "Публикую короткие атмосферные ролики и визуальные зарисовки.",
        "role": "user",
        "moods": ["laugh", "inspiration"],
    },
    {
        "username": "dark_coder",
        "email": "dark_coder@example.com",
        "bio": "Технологии, факты, знания и немного спокойствия.",
        "role": "user",
        "moods": ["knowledge", "inspiration"],
    },
    {
        "username": "calm_horizon",
        "email": "calm_horizon@example.com",
        "bio": "Контент для расслабления, природы и отдыха.",
        "role": "user",
        "moods": ["peace"],
    },
    {
        "username": "ocean_echo",
        "email": "ocean_echo@example.com",
        "bio": "Море, глубина, плавные кадры и красивое настроение.",
        "role": "user",
        "moods": ["peace", "inspiration"],
    },
    {
        "username": "sky_traveler",
        "email": "sky_traveler@example.com",
        "bio": "Путешествия, высота, динамика и красивые виды.",
        "role": "user",
        "moods": ["adrenaline", "inspiration"],
    },
    {
        "username": "fact_orbit",
        "email": "fact_orbit@example.com",
        "bio": "Короткие знания, наука, космос и интересные факты.",
        "role": "user",
        "moods": ["knowledge"],
    },
    {
        "username": "rush_vector",
        "email": "rush_vector@example.com",
        "bio": "Скорость, экстрим и заряд энергии.",
        "role": "user",
        "moods": ["adrenaline"],
    },
]

MOOD_LABELS = {
    "laugh": "Смех",
    "knowledge": "Знания",
    "peace": "Покой",
    "adrenaline": "Адреналин",
    "inspiration": "Вдохновение",
}

MOOD_KEYWORDS = {
    "laugh": [
        "funny", "cat", "dog", "dogs", "cats", "pet", "pets", "laugh",
        "kitten", "puppy", "animal", "animals", "fail", "cute"
    ],
    "knowledge": [
        "fact", "facts", "science", "space", "planet", "planets", "universe",
        "cosmos", "knowledge", "learn", "educational", "solar", "nasa"
    ],
    "peace": [
        "relax", "relaxing", "calm", "rain", "nature", "forest", "water",
        "river", "ocean", "sea", "sounds", "ambient", "meditation", "sleep",
        "peace", "quiet", "landscape"
    ],
    "adrenaline": [
        "extreme", "sport", "sports", "parkour", "fpv", "stunt", "race",
        "speed", "bike", "surf", "skate", "ski", "jump", "highlights"
    ],
    "inspiration": [
        "drone", "travel", "cinematic", "journey", "world", "city", "paris",
        "venice", "china", "iceland", "mountain", "mallorca", "switzerland",
        "beautiful", "views", "footage"
    ],
}

SUBJECT_RULES = [
    (["cat", "cats", "dog", "dogs", "pet", "pets", "kitten", "puppy"], "коты и собаки"),
    (["space", "planet", "planets", "universe", "cosmos", "nasa", "science", "fact", "facts"], "интересные факты о космосе"),
    (["rain", "ambient"], "дождь и тишина"),
    (["river"], "река и спокойствие"),
    (["ocean", "sea"], "океан и глубина"),
    (["forest"], "лес и тишина"),
    (["drone", "travel", "journey"], "путешествие с высоты"),
    (["fpv"], "полёт на скорости"),
    (["extreme", "sport", "sports", "parkour", "skate", "bike", "surf", "ski"], "экстрим и движение"),
    (["city", "paris", "venice", "china", "mallorca", "switzerland", "iceland"], "город и путешествие"),
    (["nature", "landscape", "beautiful", "views", "footage"], "природа без спешки"),
]

TITLE_TEMPLATES = {
    "peace": [
        "Тихий ритм: {subject}",
        "Короткая пауза — {subject}",
        "Спокойствие в кадре: {subject}",
        "Немного тишины: {subject}",
        "Покой и атмосфера: {subject}",
    ],
    "inspiration": [
        "Вдохновение: {subject}",
        "{subject}, которое хочется пересмотреть",
        "Короткий взгляд на {subject}",
        "Эстетика момента: {subject}",
        "Красота в движении: {subject}",
    ],
    "knowledge": [
        "Быстро и интересно: {subject}",
        "Минутка знаний: {subject}",
        "{subject} — коротко и ясно",
        "Факты за минуту: {subject}",
        "Небольшой разбор: {subject}",
    ],
    "laugh": [
        "Смешной момент: {subject}",
        "Немного смеха: {subject}",
        "{subject}, который поднимет настроение",
        "Короткое видео для улыбки: {subject}",
        "Весёлый ролик: {subject}",
    ],
    "adrenaline": [
        "Энергия движения: {subject}",
        "Короткий заряд адреналина: {subject}",
        "{subject} на максимуме",
        "Скорость и драйв: {subject}",
        "Динамика в кадре: {subject}",
    ],
}

DESCRIPTION_TEMPLATES = {
    "peace": [
        "Неспешный ролик для отдыха, спокойствия и короткой перезагрузки.",
        "Видео с мягким ритмом и атмосферой, которое помогает немного замедлиться.",
        "Небольшая визуальная пауза для тех, кто хочет выдохнуть и отвлечься.",
    ],
    "inspiration": [
        "Короткий вдохновляющий ролик с красивой картинкой и лёгким настроением.",
        "Видео, которое хочется досмотреть до конца и сохранить в закладки.",
        "Небольшая визуальная подборка для вдохновения и хорошего настроения.",
    ],
    "knowledge": [
        "Короткое познавательное видео с интересной темой и понятной подачей.",
        "Небольшой ролик, где можно быстро узнать что-то любопытное.",
        "Информация в коротком формате — без лишнего шума.",
    ],
    "laugh": [
        "Небольшой весёлый ролик для хорошего настроения и улыбки.",
        "Короткое смешное видео, которое можно переслать друзьям.",
        "Немного лёгкого контента, чтобы отвлечься и посмеяться.",
    ],
    "adrenaline": [
        "Динамичный короткий ролик с ощущением скорости, движения и энергии.",
        "Видео с бодрым ритмом, которое сразу даёт заряд адреналина.",
        "Короткий, но насыщенный ролик для тех, кто любит драйв.",
    ],
}

MOOD_TAGS = {
    "peace": ["релакс", "спокойствие", "атмосфера", "покой"],
    "inspiration": ["вдохновение", "эстетика", "красота", "кадры"],
    "knowledge": ["факты", "знания", "интересно", "обучение"],
    "laugh": ["смех", "смешно", "настроение", "юмор"],
    "adrenaline": ["экстрим", "скорость", "драйв", "энергия"],
}

COMMENT_POOLS = {
    "peace": [
        "Очень расслабляет, прям хороший ролик.",
        "Вот такое можно спокойно смотреть вечером.",
        "Нравится, как передано настроение.",
        "Приятная атмосфера, без лишней суеты.",
        "Красиво и спокойно, зашло.",
    ],
    "inspiration": [
        "Очень красивый ролик, хочется ещё.",
        "Хорошая картинка и настроение.",
        "Вот это прямо вдохновляет.",
        "Поймал вайб с первых секунд.",
        "Смотрится очень приятно.",
    ],
    "knowledge": [
        "Коротко и интересно, люблю такой формат.",
        "Полезный ролик, спасибо.",
        "Нормально подано, без воды.",
        "Интересная тема, жду ещё подобное.",
        "Вот за такие видео уважаю.",
    ],
    "laugh": [
        "Ахах, вот это смешно получилось.",
        "Подняло настроение, спасибо.",
        "Реально улыбнуло.",
        "Такое можно друзьям пересылать.",
        "Ну это сильно 😄",
    ],
    "adrenaline": [
        "Энергия чувствуется с первых секунд.",
        "Очень бодрый ролик, круто.",
        "Смотрится на одном дыхании.",
        "Есть драйв, это чувствуется.",
        "Вот это уже заряжает.",
    ],
}

REPLY_POOLS = {
    "peace": [
        "Да, тут очень мягкая атмосфера.",
        "Согласен, хорошо расслабляет.",
        "Тоже это почувствовал.",
        "Именно, очень спокойный ролик.",
    ],
    "inspiration": [
        "Да, визуал тут реально сильный.",
        "Согласен, красиво собрано.",
        "Тоже понравилось настроение.",
        "Есть в этом что-то цепляющее.",
    ],
    "knowledge": [
        "Да, формат хороший и быстрый.",
        "Согласен, тема интересная.",
        "Вот бы ещё подобного контента.",
        "Тоже люблю короткие познавательные ролики.",
    ],
    "laugh": [
        "Да, момент прям удачный.",
        "Согласен, настроение поднимает.",
        "Вот такие ролики и нужны иногда.",
        "Тоже улыбнуло 😄",
    ],
    "adrenaline": [
        "Да, очень бодро вышло.",
        "Согласен, хорошая динамика.",
        "Тоже люблю такой темп.",
        "Сразу захотелось ещё посмотреть.",
    ],
}


def stable_rng(value: str) -> random.Random:
    digest = hashlib.md5(value.encode("utf-8")).hexdigest()
    seed = int(digest[:12], 16)
    return random.Random(seed)


def load_import_state():
    os.makedirs(os.path.dirname(IMPORT_STATE_FILE), exist_ok=True)

    if not os.path.exists(IMPORT_STATE_FILE):
        return {"imported_files": []}

    try:
        with open(IMPORT_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"imported_files": []}
            data.setdefault("imported_files", [])
            return data
    except Exception:
        return {"imported_files": []}


def save_import_state(state):
    os.makedirs(os.path.dirname(IMPORT_STATE_FILE), exist_ok=True)
    with open(IMPORT_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_demo_files():
    if not os.path.exists(DEMO_FOLDER):
        print(f"❌ Папка demo_videos не найдена: {DEMO_FOLDER}")
        return []

    result = []
    for name in os.listdir(DEMO_FOLDER):
        lower = name.lower()
        if lower.endswith(".mp4") and not lower.endswith(".mp4.part"):
            result.append(os.path.join(DEMO_FOLDER, name))

    return sorted(result)


def create_users():
    users = []

    for data in USERS_DATA:
        user = User.query.filter_by(username=data["username"]).first()
        if not user:
            user = User(
                username=data["username"],
                email=data["email"],
                bio=data["bio"],
                role=data["role"],
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

        for target in others[: random.randint(2, min(4, len(others)))]:
            if not user.is_following(target):
                user.follow(target)

    db.session.commit()


def detect_mood(filename: str) -> str:
    lower = filename.lower()

    scores = {
        "laugh": 0,
        "knowledge": 0,
        "peace": 0,
        "adrenaline": 0,
        "inspiration": 0,
    }

    for mood, keywords in MOOD_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                scores[mood] += 1

    best_mood = max(scores, key=scores.get)
    if scores[best_mood] == 0:
        return "inspiration"
    return best_mood


def detect_subject(filename: str) -> str:
    lower = filename.lower()

    for keywords, subject in SUBJECT_RULES:
        for kw in keywords:
            if kw in lower:
                return subject

    return "интересный ролик"


def build_metadata_from_filename(filename: str):
    mood = detect_mood(filename)
    subject = detect_subject(filename)
    rng = stable_rng(filename)

    title = rng.choice(TITLE_TEMPLATES[mood]).format(subject=subject)
    description = rng.choice(DESCRIPTION_TEMPLATES[mood])

    base_tags = MOOD_TAGS[mood][:]

    subject_tags = []
    lower = filename.lower()

    if any(x in lower for x in ["cat", "dog", "pet", "animal"]):
        subject_tags += ["животные", "питомцы"]
    if any(x in lower for x in ["space", "planet", "cosmos", "science", "fact"]):
        subject_tags += ["космос", "наука"]
    if any(x in lower for x in ["rain", "forest", "river", "ocean", "sea", "nature", "landscape"]):
        subject_tags += ["природа"]
    if any(x in lower for x in ["drone", "travel", "journey", "city", "venice", "paris", "china"]):
        subject_tags += ["путешествие"]
    if any(x in lower for x in ["extreme", "sport", "fpv", "parkour", "surf", "bike", "skate"]):
        subject_tags += ["спорт"]

    tags = []
    for tag in base_tags + subject_tags:
        if tag not in tags:
            tags.append(tag)

    if subject == "коты и собаки" and "юмор" not in tags:
        tags.append("юмор")
    if subject == "интересные факты о космосе" and "факты" not in tags:
        tags.append("факты")

    tags = tags[:5]

    return {
        "title": title,
        "description": description,
        "mood": mood,
        "tags": ", ".join(tags),
        "subject": subject,
    }


def choose_author_for_mood(users, mood, filename):
    suited = [u for u in users if mood in next(item["moods"] for item in USERS_DATA if item["username"] == u.username)]
    if suited:
        rng = stable_rng(filename + mood)
        return suited[rng.randint(0, len(suited) - 1)]
    return random.choice(users)


def make_unique_title(title):
    if not Video.query.filter_by(title=title).first():
        return title

    i = 2
    while True:
        candidate = f"{title} #{i}"
        if not Video.query.filter_by(title=candidate).first():
            return candidate
        i += 1


def choose_main_filename(qualities):
    for q in ["1080p", "720p", "480p", "360p", "240p"]:
        if q in qualities:
            return qualities[q]
    return next(iter(qualities.values()), None)


def import_video_file(source_path, author, meta, upload_folder):
    videos_folder = os.path.join(upload_folder, "videos")
    os.makedirs(videos_folder, exist_ok=True)

    base_name = secrets_token(source_path)

    print(f"\n🎬 Импорт файла: {os.path.basename(source_path)}")
    print(f"   Автор: {author.username}")
    print(f"   Mood: {meta['mood']} ({MOOD_LABELS[meta['mood']]})")
    print(f"   Название: {meta['title']}")

    qualities = convert_video_all_qualities(
        input_path=source_path,
        base_filename=base_name,
        videos_folder=videos_folder,
    )

    if not qualities:
        print("   ❌ Не удалось сконвертировать видео")
        return None

    main_filename = choose_main_filename(qualities)
    if not main_filename:
        print("   ❌ Не удалось выбрать основной файл")
        return None

    thumbnail = generate_thumbnail(main_filename)

    rng = stable_rng(os.path.basename(source_path))
    created_at = datetime.utcnow() - timedelta(
        days=rng.randint(0, 35),
        hours=rng.randint(0, 23),
        minutes=rng.randint(0, 59),
    )

    views = rng.randint(25, 650)

    video = Video(
        title=make_unique_title(meta["title"]),
        description=meta["description"],
        filename=main_filename,
        thumbnail=thumbnail,
        user_id=author.id,
        mood=meta["mood"],
        tags=meta["tags"],
        visibility="public",
        views=views,
        karma=0,
        qualities=json.dumps(qualities, ensure_ascii=False),
        created_at=created_at,
    )

    db.session.add(video)
    db.session.commit()

    print(f"   ✅ Видео создано: ID={video.id}")
    return video


def add_video_reactions(video, users):
    rng = stable_rng(video.title + "_reactions")
    shuffled = users[:]
    rng.shuffle(shuffled)

    count = rng.randint(2, min(6, len(shuffled)))
    selected = shuffled[:count]

    weights_map = {
        "laugh": [55, 35, 10],
        "knowledge": [25, 65, 10],
        "peace": [20, 70, 10],
        "adrenaline": [60, 30, 10],
        "inspiration": [45, 45, 10],
    }

    weights = weights_map.get(video.mood, [40, 50, 10])

    used = 0
    for user in selected:
        if Reaction.query.filter_by(user_id=user.id, video_id=video.id).first():
            continue

        reaction_type = rng.choices(
            population=["fire", "good", "bad"],
            weights=weights,
            k=1
        )[0]

        reaction = Reaction(
            reaction_type=reaction_type,
            user_id=user.id,
            video_id=video.id,
            created_at=video.created_at + timedelta(minutes=rng.randint(10, 500)),
        )
        db.session.add(reaction)
        used += 1

    db.session.commit()
    video.recalculate_karma()
    db.session.commit()
    return used


def add_comments_and_replies(video, users):
    rng = stable_rng(video.title + "_comments")
    comment_pool = COMMENT_POOLS.get(video.mood, COMMENT_POOLS["inspiration"])
    reply_pool = REPLY_POOLS.get(video.mood, REPLY_POOLS["inspiration"])

    authors = users[:]
    rng.shuffle(authors)

    comment_count = rng.randint(2, 6)
    created = 0

    for i in range(comment_count):
        author = authors[i % len(authors)]

        comment = Comment(
            text=rng.choice(comment_pool),
            user_id=author.id,
            video_id=video.id,
            created_at=video.created_at + timedelta(minutes=rng.randint(15, 900)),
        )
        db.session.add(comment)
        db.session.flush()
        created += 1

        reactors = users[:]
        rng.shuffle(reactors)

        for reactor in reactors[:rng.randint(0, 3)]:
            if reactor.id == author.id:
                continue

            if CommentReaction.query.filter_by(user_id=reactor.id, comment_id=comment.id).first():
                continue

            comment_reaction = CommentReaction(
                reaction_type=rng.choices(
                    population=["like", "dislike"],
                    weights=[85, 15],
                    k=1
                )[0],
                user_id=reactor.id,
                comment_id=comment.id,
                created_at=comment.created_at + timedelta(minutes=rng.randint(1, 60)),
            )
            db.session.add(comment_reaction)

        reply_users = users[:]
        rng.shuffle(reply_users)

        for reply_author in reply_users[:rng.randint(0, 2)]:
            reply = CommentReply(
                text=rng.choice(reply_pool),
                user_id=reply_author.id,
                comment_id=comment.id,
                created_at=comment.created_at + timedelta(minutes=rng.randint(3, 120)),
            )
            db.session.add(reply)

    db.session.commit()
    return created


def add_watch_history(video, users):
    rng = stable_rng(video.title + "_history")
    watchers = users[:]
    rng.shuffle(watchers)

    count = rng.randint(2, min(8, len(watchers)))
    created = 0

    for user in watchers[:count]:
        item = WatchHistory(
            user_id=user.id,
            video_id=video.id,
            watched_at=video.created_at + timedelta(minutes=rng.randint(20, 1440)),
        )
        db.session.add(item)
        created += 1

    db.session.commit()
    return created


def secrets_token(source_path):
    digest = hashlib.md5(os.path.basename(source_path).encode("utf-8")).hexdigest()
    return digest[:32]


def main():
    print("=" * 80)
    print("ЗАПОЛНЕНИЕ LAMPIX ДЕМО-КОНТЕНТОМ")
    print("=" * 80)

    files = get_demo_files()
    if not files:
        print("❌ В папке demo_videos нет готовых .mp4 файлов")
        return

    state = load_import_state()
    imported_files = set(state.get("imported_files", []))

    print(f"Найдено mp4 файлов: {len(files)}")

    pending_files = []
    for file_path in files:
        base = os.path.basename(file_path)
        if base not in imported_files:
            pending_files.append(file_path)

    print(f"Новых для импорта: {len(pending_files)}")

    if not pending_files:
        print("✅ Все файлы из demo_videos уже были импортированы ранее")
        print("Если хочешь импортировать заново — удали файл instance/seed_demo_imports.json")
        return

    answer = input("\nСоздать демо-контент? (yes/no): ").strip().lower()
    if answer not in ("yes", "y", "да"):
        print("⏭️ Отменено")
        return

    users = create_users()
    create_subscriptions(users)

    print(f"\n✅ Пользователи готовы: {len(users)}")
    print("Пароль для всех демо-пользователей: Demo123")

    upload_folder = app.config["UPLOAD_FOLDER"]

    imported_count = 0
    failed_count = 0

    for index, source_path in enumerate(pending_files, start=1):
        base = os.path.basename(source_path)
        meta = build_metadata_from_filename(base)
        author = choose_author_for_mood(users, meta["mood"], base)

        print(f"\n[{index}/{len(pending_files)}] {base}")

        try:
            video = import_video_file(source_path, author, meta, upload_folder)
            if not video:
                failed_count += 1
                continue

            reactions_count = add_video_reactions(video, users)
            comments_count = add_comments_and_replies(video, users)
            history_count = add_watch_history(video, users)

            print(f"   👍 Реакции: {reactions_count}")
            print(f"   💬 Комментарии: {comments_count}")
            print(f"   👁 История просмотров: {history_count}")

            imported_files.add(base)
            state["imported_files"] = sorted(imported_files)
            save_import_state(state)

            imported_count += 1

        except Exception as e:
            failed_count += 1
            db.session.rollback()
            print(f"   ❌ Ошибка импорта: {e}")

    print("\n" + "=" * 80)
    print("ГОТОВО")
    print("=" * 80)
    print(f"Импортировано: {imported_count}")
    print(f"Ошибок:        {failed_count}")
    print(f"Всего файлов:  {len(files)}")
    print(f"В архиве:      {len(imported_files)}")
    print("=" * 80)
    print("Пользователи:")
    for user in users:
        print(f" - {user.username}")
    print("=" * 80)


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        main()