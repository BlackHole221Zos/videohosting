# test_email.py

from app import create_app
from app.extensions import mail
from flask_mail import Message

app = create_app()

with app.app_context():
    print("=" * 50)
    print("📧 Проверка настроек email...")
    print("=" * 50)
    print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
    print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
    print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"MAIL_PASSWORD: {'*' * 16 if app.config['MAIL_PASSWORD'] else 'НЕ УСТАНОВЛЕН!'}")

    try:
        msg = Message(
            subject='Тест VidSphere',
            recipients=[app.config['MAIL_USERNAME']],
            body='Если ты получил это письмо — всё работает!'
        )
        mail.send(msg)
        print("\n✅ ПИСЬМО ОТПРАВЛЕНО! Проверь почту.")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")