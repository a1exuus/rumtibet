import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

import csv
import io

import telebot
from telebot import types
from django.db.models import Count
from environs import Env

from core.models import ContactForm


env = Env()
env.read_env()
token = env('TG_BOT_TOKEN')

bot = telebot.TeleBot(token)
ADMIN_ID = int(env('TG_CHAT_ID'))

TYPE_LABELS = dict(ContactForm._meta.get_field('form_type').choices)


def admin_only(handler):
    def wrapper(message):
        if message.chat.id != ADMIN_ID:
            bot.reply_to(message, '⛔ Этот бот приватный.')
            return
        handler(message)
    return wrapper


def lead_text(lead):
    return (
        f"📨 Заявка #{lead.pk} · {TYPE_LABELS.get(lead.form_type, lead.form_type)}\n"
        f"👤 Имя: {lead.name}\n"
        f"📞 Телефон: {lead.phone or '—'}\n"
        f"✉️ Email: {lead.email or '—'}\n"
        f"💬 Комментарий: {lead.comment or '—'}\n"
        f"🕒 {lead.created_at:%d.%m.%Y %H:%M}"
    )


@bot.message_handler(commands=['start'])
@admin_only
def start(message):
    bot.send_message(
        message.chat.id,
        '🏔 РумТибет-бот на связи!\n\n'
        '/leads — новые заявки\n'
        '/all — последние 20 заявок\n'
        '/stats — статистика\n'
        '/export — выгрузка в CSV',
    )


@bot.message_handler(commands=['leads'])
@admin_only
def leads(message):
    items = ContactForm.objects.filter(is_processed=False).order_by('-created_at')[:10]
    if not items:
        bot.send_message(message.chat.id, 'Новых заявок нет 🎉')
        return
    for lead in items:
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton('✅ Обработано', callback_data=f'done:{lead.pk}'))
        bot.send_message(message.chat.id, lead_text(lead), reply_markup=kb)


@bot.message_handler(commands=['all'])
@admin_only
def all_leads(message):
    items = ContactForm.objects.order_by('-created_at')[:20]
    if not items:
        bot.send_message(message.chat.id, 'Заявок пока нет.')
        return
    for lead in items:
        status = '✅' if lead.is_processed else '🆕'
        bot.send_message(message.chat.id, f'{status} {lead_text(lead)}')


@bot.message_handler(commands=['stats'])
@admin_only
def stats(message):
    total = ContactForm.objects.count()
    new = ContactForm.objects.filter(is_processed=False).count()
    lines = [f'📊 Всего заявок: {total}', f'🆕 Необработанных: {new}', '', 'По типам:']
    for row in ContactForm.objects.values('form_type').annotate(n=Count('id')):
        lines.append(f'• {TYPE_LABELS.get(row["form_type"], row["form_type"])}: {row["n"]}')
    bot.send_message(message.chat.id, '\n'.join(lines))


@bot.message_handler(commands=['export'])
@admin_only
def export(message):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(['ID', 'Тип', 'Имя', 'Телефон', 'Email', 'Комментарий', 'Дата', 'Обработано'])
    for lead in ContactForm.objects.order_by('-created_at'):
        w.writerow([
            lead.pk, lead.form_type, lead.name, lead.phone or '', lead.email or '',
            lead.comment or '', lead.created_at.strftime('%d.%m.%Y %H:%M'),
            'да' if lead.is_processed else 'нет',
        ])
    # utf-8-sig, чтобы Excel открыл кириллицу без кракозябр
    bot.send_document(message.chat.id, ('leads.csv', buf.getvalue().encode('utf-8-sig'), 'text/csv'))


@bot.callback_query_handler(func=lambda c: c.data.startswith('done:'))
def done(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, '⛔', show_alert=True)
        return
    pk = int(call.data.split(':')[1])
    ContactForm.objects.filter(pk=pk).update(is_processed=True)
    bot.answer_callback_query(call.id, 'Заявка обработана ✅')
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)


if __name__ == '__main__':
    print('Бот запущен...')
    bot.infinity_polling(skip_pending=True)