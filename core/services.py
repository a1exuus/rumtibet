import requests
from django.conf import settings


def notify_telegram(text: str, lead_id: int = None):
    payload = {'chat_id': settings.TG_CHAT_ID, 'text': text}
    if lead_id:
        payload['reply_markup'] = {
            'inline_keyboard': [[{'text': '✅ Обработано', 'callback_data': f'done:{lead_id}'}]]
        }
    try:
        requests.post(
            f'https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage',
            json=payload, timeout=5,
        )
    except requests.RequestException:
        pass