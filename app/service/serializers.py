from rest_framework import serializers

from .models import Mailing, Client, Message


class MailingSerializer(serializers.ModelSerializer):
    def validate(self, data):
        errors = {}
        if data['begin'] > data['end']:
            errors['non_field_errors'] = serializers.ValidationError('Время начала рассылки позже времени окончания')

        if errors:
            raise serializers.ValidationError(errors)
        return data

    class Meta:
        model = Mailing
        fields = ('id', 'begin', 'message', 'filters', 'end')


class ClientSerializer(serializers.ModelSerializer):
    def validate(self, data):
        data['operator_code'] = data['phone'][1:4]
        return data

    class Meta:
        model = Client
        fields = ('id', 'phone', 'operator_code', 'tag', 'timezone')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'datetime', 'status', 'mailing', 'client')
