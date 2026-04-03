# create_placeholders.py
# Запусти: python create_placeholders.py

import os

# Папка для картинок
img_dir = 'app/static/img'
os.makedirs(img_dir, exist_ok=True)

# SVG аватар
avatar_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <rect width="200" height="200" fill="#1a1a2e"/>
  <circle cx="100" cy="70" r="35" fill="#4ecdc4"/>
  <ellipse cx="100" cy="160" rx="55" ry="45" fill="#4ecdc4"/>
</svg>'''

# SVG превью видео
thumb_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180">
  <rect width="320" height="180" fill="#12121a"/>
  <polygon points="130,55 130,125 190,90" fill="#4ecdc4"/>
</svg>'''

# Сохраняем
with open(os.path.join(img_dir, 'default_avatar.svg'), 'w') as f:
    f.write(avatar_svg)
    print('✅ Создан: default_avatar.svg')

with open(os.path.join(img_dir, 'default_thumb.svg'), 'w') as f:
    f.write(thumb_svg)
    print('✅ Создан: default_thumb.svg')

# Также создаём .png версии через копирование (браузеры понимают SVG)
# Для полной совместимости можно конвертировать через Pillow/cairosvg

print('\n🎉 Заглушки созданы!')
print('Если нужны PNG — конвертируй SVG онлайн или через Pillow')