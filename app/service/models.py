from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models


class Mailing(models.Model):
    begin = models.DateTimeField(verbose_name='начало рассылки')
    message = models.TextField(verbose_name='текст сообщения')
    filters = models.JSONField(verbose_name='фильтр свойств клиентов')
    end = models.DateTimeField(verbose_name='окончаниe рассылки')

    def __repr__(self):
        return self.message

    def clean(self):
        super().clean()

        errors = {}
        if self.begin > self.end:
            errors[NON_FIELD_ERRORS] = ValidationError('Время начала рассылки позже времени окончания')

    def get_clients(self):
        temp_qs_list = []
        out = Client.objects.all()
        try:
            operator_code = self.filters['operator_code']
            out = Client.objects.filter(operator_code=str(operator_code))
        except KeyError:
            pass

        try:
            filters = self.filters['filters']  # type: list
            for i in filters:
                temp_qs_list.append(Client.objects.filter(tag=i))
        except KeyError:
            pass

        if temp_qs_list:
            out = out.intersection(*temp_qs_list)

        return out

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class Client(models.Model):
    import pytz
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    phone = models.CharField(max_length=11,
                             unique=True,
                             validators=[
                                 MinLengthValidator(11),
                                 RegexValidator(regex=r'7\d{10}', message='Номер телефона не соотвествует '
                                                                          'формату 7XXXXXXXXXX')],
                             help_text='номер телефона в формате 7XXXXXXXXXX (X - цифра от 0 до 9)',
                             verbose_name='номер телефона')
    operator_code = models.CharField(max_length=3, editable=False, verbose_name='код мобильного оператора')
    tag = models.CharField(max_length=20, verbose_name='тег (произвольная метка)')
    timezone = models.CharField(max_length=32, choices=TIMEZONES, default='UTC', verbose_name='часовой пояс')

    def __repr__(self):
        return self.phone

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Message(models.Model):
    class Status(models.TextChoices):
        CREATED = 'c', 'Создано'
        SHIPPED = 's', 'Отправлено'
        DELIVERED = 'd', 'Доставлено'
        __empty__ = 'Статус сообщения'

    datetime = models.DateTimeField(verbose_name='дата и время создания (отправки)')
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.CREATED, editable=False,
                              verbose_name='статус отправки')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='message_mailing', verbose_name='Рассылка')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='message_client', verbose_name='Клиент')

    def __repr__(self):
        return self.status + ' - ' + self.datetime.__repr__()

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
