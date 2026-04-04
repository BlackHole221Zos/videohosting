# app/models.py

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

import secrets
from datetime import timedelta

# ============ ТАБЛИЦА ПОДПИСОК (many-to-many) ============

subscriptions = db.Table('subscriptions',
                         db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                         db.Column('following_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                         db.Column('created_at', db.DateTime, default=datetime.utcnow)
                         )


# ============ ПОЛЬЗОВАТЕЛЬ ============

class User(db.Model):
    """Модель пользователя"""

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # Роль: user, moderator, admin
    role = db.Column(db.String(20), default='user', nullable=False)

    # Профиль
    avatar = db.Column(db.String(255), default='default_avatar.png')
    bio = db.Column(db.Text, default='')

    # Даты
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    videos = db.relationship('Video', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    reactions = db.relationship('Reaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    watch_history = db.relationship('WatchHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    # Подписки (на кого подписан)
    following = db.relationship(
        'User',
        secondary=subscriptions,
        primaryjoin=(subscriptions.c.follower_id == id),
        secondaryjoin=(subscriptions.c.following_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    # ===== Методы пароля =====

    def set_password(self, password):
        """Хеширует и сохраняет пароль"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверяет пароль"""
        return check_password_hash(self.password_hash, password)

    # ===== Методы подписок =====

    def follow(self, user):
        """Подписаться на пользователя"""
        if not self.is_following(user) and self.id != user.id:
            self.following.append(user)

    def unfollow(self, user):
        """Отписаться от пользователя"""
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        """Проверяет подписку"""
        return self.following.filter(subscriptions.c.following_id == user.id).count() > 0

    def followers_count(self):
        """Количество подписчиков"""
        return self.followers.count()

    def following_count(self):
        """Количество подписок"""
        return self.following.count()

    # ===== Статистика =====

    def total_views(self):
        """Общее количество просмотров всех видео"""
        return sum(video.views for video in self.videos)

    def total_karma(self):
        """Общая карма всех видео"""
        return sum(video.karma for video in self.videos)

    # ===== Проверка ролей =====

    def is_admin(self):
        return self.role == 'admin'

    def is_moderator(self):
        return self.role in ['admin', 'moderator']

    def __repr__(self):
        return f'<User {self.username}>'


# ============ ВИДЕО ============

class Video(db.Model):
    """Модель видео"""

    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')

    # Файлы
    filename = db.Column(db.String(255), nullable=False)  # Имя видеофайла
    thumbnail = db.Column(db.String(255), default='default_thumb.jpg')  # Превью

    # Автор
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    # Mood (настроение)
    # laugh, knowledge, peace, adrenaline, inspiration
    mood = db.Column(db.String(50), default='inspiration')

    # Теги (через запятую)
    tags = db.Column(db.String(500), default='')

    # Статистика
    views = db.Column(db.Integer, default=0)
    karma = db.Column(db.Integer, default=0)

    # Даты
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Связи
    comments = db.relationship('Comment', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    reactions = db.relationship('Reaction', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    watch_history = db.relationship('WatchHistory', backref='video', lazy='dynamic', cascade='all, delete-orphan')

    # ===== Методы =====

    def get_tags_list(self):
        """Возвращает список тегов"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    def hot_score(self):
        """Алгоритм трендов: karma / age^1.5"""
        age_hours = (datetime.utcnow() - self.created_at).total_seconds() / 3600
        age_hours = max(age_hours, 1)  # Минимум 1 час
        return self.karma / (age_hours ** 1.5)

    def mood_emoji(self):
        """Возвращает эмодзи для настроения"""
        moods = {
            'laugh': '😂',
            'knowledge': '🧠',
            'peace': '🌸',
            'adrenaline': '⚡',
            'inspiration': '✨'
        }
        return moods.get(self.mood, '🎬')

    def mood_name(self):
        """Возвращает название настроения"""
        moods = {
            'laugh': 'Смех',
            'knowledge': 'Знания',
            'peace': 'Покой',
            'adrenaline': 'Адреналин',
            'inspiration': 'Вдохновение'
        }
        return moods.get(self.mood, 'Видео')

    def recalculate_karma(self):
        """Пересчитывает карму на основе реакций"""
        karma_values = {'fire': 3, 'good': 1, 'bad': -1}
        total = 0
        for reaction in self.reactions:
            total += karma_values.get(reaction.reaction_type, 0)
        self.karma = total
        return self.karma

    def __repr__(self):
        return f'<Video {self.title}>'


# ============ КОММЕНТАРИЙ ============

class Comment(db.Model):
    """Модель комментария"""

    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

    # Связи
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

    # Дата
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Comment by {self.author.username}>'


# ============ РЕАКЦИЯ (КАРМА) ============

class Reaction(db.Model):
    """Модель реакции (карма)

    fire = 🔥 (+3 кармы)
    good = 👍 (+1 карма)
    bad  = 👎 (-1 карма)
    """

    __tablename__ = 'reaction'

    id = db.Column(db.Integer, primary_key=True)

    # Тип: fire, good, bad
    reaction_type = db.Column(db.String(10), nullable=False)

    # Связи
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

    # Дата
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Один пользователь — одна реакция на видео
    __table_args__ = (
        db.UniqueConstraint('user_id', 'video_id', name='unique_user_video_reaction'),
    )

    def karma_value(self):
        """Возвращает значение кармы"""
        values = {'fire': 3, 'good': 1, 'bad': -1}
        return values.get(self.reaction_type, 0)

    def __repr__(self):
        return f'<Reaction {self.reaction_type}>'


# ============ ИСТОРИЯ ПРОСМОТРОВ ============

class WatchHistory(db.Model):
    """История просмотров (для рекомендаций)"""

    __tablename__ = 'watch_history'

    id = db.Column(db.Integer, primary_key=True)

    # Связи
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

    # Дата просмотра
    watched_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WatchHistory user={self.user_id} video={self.video_id}>'


# ============ ТОКЕН ВОССТАНОВЛЕНИЯ ПАРОЛЯ ============

class PasswordResetToken(db.Model):
    """Токен для восстановления пароля"""

    __tablename__ = 'password_reset_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    # Связь с пользователем
    user = db.relationship('User', backref='reset_tokens')

    @staticmethod
    def generate_token():
        """Генерирует случайный токен"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_for_user(user):
        """Создаёт токен для пользователя (действует 1 час)"""
        # Удаляем старые токены этого пользователя
        PasswordResetToken.query.filter_by(user_id=user.id).delete()

        token = PasswordResetToken(
            user_id=user.id,
            token=PasswordResetToken.generate_token(),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.session.add(token)
        db.session.commit()
        return token

    def is_expired(self):
        """Проверяет истёк ли токен"""
        return datetime.utcnow() > self.expires_at

    @staticmethod
    def verify_token(token_string):
        """Проверяет токен и возвращает пользователя или None"""
        token = PasswordResetToken.query.filter_by(token=token_string).first()

        if not token:
            return None

        if token.is_expired():
            db.session.delete(token)
            db.session.commit()
            return None

        return token.user

    def __repr__(self):
        return f'<PasswordResetToken user={self.user.username}>'

# ============ ФУНКЦИЯ ИНИЦИАЛИЗАЦИИ БД ============

def init_db(app):
    """
    Инициализирует БД и создаёт админа если его нет.
    Вызывается при старте приложения.
    Не удаляет существующие данные!
    """
    with app.app_context():
        # Создаём таблицы (если не существуют)
        db.create_all()

        # Проверяем есть ли админ
        admin = User.query.filter_by(role='admin').first()

        if not admin:
            # Создаём администратора
            admin = User(
                username='admin',
                email='admin@vidsphere.com',
                role='admin',
                bio='Администратор VidSphere'
            )
            admin.set_password('Admin123')  # Пароль по умолчанию

            db.session.add(admin)
            db.session.commit()

            print('=' * 50)
            print('🔐 СОЗДАН АДМИНИСТРАТОР:')
            print('   Логин: admin')
            print('   Пароль: Admin123')
            print('   ⚠️  СМЕНИТЕ ПАРОЛЬ ПОСЛЕ ПЕРВОГО ВХОДА!')
            print('=' * 50)
        else:
            print(f'✅ Админ существует: {admin.username}')