# РУМТИБЕТ — горные походы и туры

Сайт туристического агентства: каталог туров, блог, заявки.

## Стек
- Django 6.0 + SQLite
- Django Admin + TinyMCE + adminsortable2
- Vanilla JS, SCSS, Next Art
- Gunicorn + Nginx + Let's Encrypt
- pyTelegramBotAPI (локальная мини-CRM)

## Локальный запуск
\```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
\```

## Продакшен-деплой
Ubuntu VPS + gunicorn (systemd) + nginx reverse-proxy + certbot.
Схема обновления кода: `git fetch && git reset --hard origin/main && collectstatic`.

## Страницы
- `/` — главная
- `/programs/` — каталог с фильтрами
- `/programs/<id>/` — детальная тура с галереей и формой заявки
- `/blog/` — статьи с пагинацией
- `/blog/<id>/` — детальная статьи
- `/admin/` — админка