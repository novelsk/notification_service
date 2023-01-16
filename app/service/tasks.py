from django.conf import settings
from django.utils import timezone
from celery import shared_task
from .models import Message
import requests


@shared_task
def send_message(message_id) -> None:
    message = Message.objects.get(id=message_id)
    if message is not None:
        response = requests.post(
            url=f'https://probe.fbrq.cloud/v1/send/{message.id}',
            headers={'Authorization': f'Bearer {settings.JWT_TOKEN}'},
            json={
                'id': message.mailing.id,
                'phone': message.client.phone,
                'message': message.mailing.message
            }
        )

        if response.status_code == 200:
            message.status = Message.Status.DELIVERED
        elif response.status_code == '400':
            print(f'status: {response.status_code}\nThe specified JWT token is outdated')
            message.status = Message.Status.SHIPPED
            send_message((message,), eta=timezone.now() + 600)
        elif response.status_code == '401':
            print(f'status: {response.status_code}\nInvalid JWT token specified')
            message.status = Message.Status.SHIPPED
            send_message((message,), eta=timezone.now() + 600)
        message.save()
    else:
        raise ValueError('object Message is None')
