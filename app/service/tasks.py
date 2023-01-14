from django.conf import settings
from celery import shared_task
import requests


@shared_task
def send_message(message_id, phone, text, mailing_id):
    response = requests.post(
        url=f'https://probe.fbrq.cloud/v1/send/{message_id}',
        headers={'Authorization': f'Bearer {settings.JWT_TOKEN}'},
        json={
            'id': mailing_id,
            'phone': phone,
            'message': text
        }
    )

    django_callback = requests.post(
        url='http://0.0.0.0:8000/celery/message/',
        json={
            'secret_key': 'secret_key',
            'id': message_id,
            'status_code': response.status_code
        }
    )
