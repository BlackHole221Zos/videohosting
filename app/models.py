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
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    avatar = db.Column(db.String(255), default='default_avatar.png')
    bio = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    videos = db.relationship('Video', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    reactions = db.relationship('Reaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    watch_history = db.relationship('WatchHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    comment_replies = db.relationship('CommentReply', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comment_reactions = db.relationship('CommentReaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    following = db.relationship(
        'User',
        secondary=subscriptions,
        primaryjoin=(subscriptions.c.follower_id == id),
        secondaryjoin=(subscriptions.c.following_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user) and self.id != user.id:
            self.following.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(subscriptions.c.following_id == user.id).count() > 0

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

    def total_views(self):
        return sum(video.views for video in self.videos)

    def total_karma(self):
        return sum(video.karma for video in self.videos)

    def is_admin(self):
        return self.role == 'admin'

    def is_moderator(self):
        return self.role in ['admin', 'moderator']

    def __repr__(self):
        return f'<User {self.username}>'


# ============ ВИДЕО ============

class Video(db.Model):
    __tablename__ = 'video'

    qualities = db.Column(db.Text, default='{}')
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    filename = db.Column(db.String(255), nullable=False)
    thumbnail = db.Column(db.String(255), default='default_thumb.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    mood = db.Column(db.String(50), default='inspiration')
    tags = db.Column(db.String(500), default='')
    visibility = db.Column(db.String(20), default='public')
    views = db.Column(db.Integer, default=0)
    karma = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    comments = db.relationship('Comment', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    reactions = db.relationship('Reaction', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    watch_history = db.relationship('WatchHistory', backref='video', lazy='dynamic', cascade='all, delete-orphan')

    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    def hot_score(self):
        age_hours = (datetime.utcnow() - self.created_at).total_seconds() / 3600
        age_hours = max(age_hours, 1)
        return self.karma / (age_hours ** 1.5)

    def mood_emoji(self):
        moods = {
            'laugh': '😂',
            'knowledge': '🧠',
            'peace': '🌸',
            'adrenaline': '⚡',
            'inspiration': '✨'
        }
        return moods.get(self.mood, '🎬')

    def mood_name(self):
        moods = {
            'laugh': 'Смех',
            'knowledge': 'Знания',
            'peace': 'Покой',
            'adrenaline': 'Адреналин',
            'inspiration': 'Вдохновение'
        }
        return moods.get(self.mood, 'Видео')

    def recalculate_karma(self):
        karma_values = {'fire': 3, 'good': 1, 'bad': -1}
        total = 0
        for reaction in self.reactions:
            total += karma_values.get(reaction.reaction_type, 0)
        self.karma = total
        return self.karma

    def get_qualities(self):
        import json
        try:
            return json.loads(self.qualities) if self.qualities else {}
        except:
            return {}

    def get_best_quality_filename(self):
        qualities = self.get_qualities()
        for q in ['1080p', '720p', '480p']:
            if q in qualities:
                return qualities[q]
        return self.filename

    def __repr__(self):
        return f'<Video {self.title}>'


# ============ КОММЕНТАРИЙ ============

class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🆕 Связи с ответами и реакциями
    replies = db.relationship('CommentReply', backref='comment', lazy='dynamic', cascade='all, delete-orphan')
    comment_reactions = db.relationship('CommentReaction', backref='comment', lazy='dynamic', cascade='all, delete-orphan')

    def likes_count(self):
        return self.comment_reactions.filter_by(reaction_type='like').count()

    def dislikes_count(self):
        return self.comment_reactions.filter_by(reaction_type='dislike').count()

    def replies_count(self):
        return self.replies.count()

    def __repr__(self):
        return f'<Comment by {self.author.username}>'


# ============ 🆕 ОТВЕТ НА КОММЕНТАРИЙ ============

class CommentReply(db.Model):
    """Ответ на комментарий"""

    __tablename__ = 'comment_reply'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CommentReply by {self.author.username}>'


# ============ 🆕 РЕАКЦИЯ НА КОММЕНТАРИЙ ============

class CommentReaction(db.Model):
    """Реакция на комментарий (лайк/дизлайк)"""

    __tablename__ = 'comment_reaction'

    id = db.Column(db.Integer, primary_key=True)
    reaction_type = db.Column(db.String(10), nullable=False)  # like / dislike
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 1 реакция от 1 юзера на 1 комментарий
    __table_args__ = (
        db.UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_reaction'),
    )

    def __repr__(self):
        return f'<CommentReaction {self.reaction_type}>'


# ============ РЕАКЦИЯ НА ВИДЕО (КАРМА) ============

class Reaction(db.Model):
    __tablename__ = 'reaction'

    id = db.Column(db.Integer, primary_key=True)
    reaction_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'video_id', name='unique_user_video_reaction'),
    )

    def karma_value(self):
        values = {'fire': 3, 'good': 1, 'bad': -1}
        return values.get(self.reaction_type, 0)

    def __repr__(self):
        return f'<Reaction {self.reaction_type}>'


# ============ ИСТОРИЯ ПРОСМОТРОВ ============

class WatchHistory(db.Model):
    __tablename__ = 'watch_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    watched_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WatchHistory user={self.user_id} video={self.video_id}>'


# ============ ТОКЕН ВОССТАНОВЛЕНИЯ ПАРОЛЯ ============

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    user = db.relationship('User', backref='reset_tokens')

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_for_user(user):
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
        return datetime.utcnow() > self.expires_at

    @staticmethod
    def verify_token(token_string):
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


# ============ ИНИЦИАЛИЗАЦИЯ БД ============

def init_db(app):
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(role='admin').first()

        if not admin:
            admin = User(
                username='admin',
                email='admin@vidsphere.com',
                role='admin',
                bio='Администратор VidSphere'
            )
            admin.set_password('Admin123')
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