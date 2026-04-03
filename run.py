# run.py

from app import create_app

# Создаём приложение
app = create_app()

if __name__ == '__main__':
    # Запуск сервера разработки
    # debug=True — автоперезагрузка при изменениях
    app.run(debug=True, host='127.0.0.1', port=5000)