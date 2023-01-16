from django.utils import timezone

from .models import Mailing, Message
from .tasks import send_message


def create_messages(mailing: Mailing):
    messages = []
    for client in mailing.get_clients():
        message = Message.objects.create(
            datetime=timezone.now(),
            mailing=mailing,
            client=client
        )
        message.save()
        messages.append(message)
    return messages


def check_mailing(mailing_id):
    mailing = Mailing.objects.get(id=mailing_id)
    messages = create_messages(mailing)
    now_time = timezone.now()

    if mailing.begin < now_time < mailing.end:
        for i in messages:
            send_message.delay(i.id)

    elif mailing.begin > now_time:
        for i in messages:
            send_message.apply_async((i.id,), eta=mailing.begin)
