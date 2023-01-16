from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Client, Mailing, Message
from .serializers import MailingSerializer, ClientSerializer, MailingMessagesSerializer
from .service import check_mailing
from .tasks import send_message

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

response_400 = openapi.Response('BAD_REQUEST')
client_response_get = openapi.Response('Client list', ClientSerializer(many=True))
client_response_post = openapi.Response('New Client', ClientSerializer)
client_response_detail_get = openapi.Response('Client object', ClientSerializer)
mailing_response_get = openapi.Response('Mailing list', MailingSerializer(many=True))
mailing_response_post = openapi.Response('New Mailing', MailingSerializer)
mailing_response_detail_get = openapi.Response('Mailing object', MailingSerializer)
mailing_statistics_response_get = openapi.Response('New Mailing', MailingMessagesSerializer(many=True))


@swagger_auto_schema(method='get', responses={200: client_response_get})
@swagger_auto_schema(method='post', request_body=ClientSerializer)
@api_view(['GET', 'POST'])
def api_client(request):
    if request.method == 'GET':
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={200: client_response_detail_get})
@swagger_auto_schema(methods=['put', 'patch'], request_body=ClientSerializer)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'GET':
        serializer = ClientSerializer(client)
        return Response(serializer.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = ClientSerializer(client, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='get', responses={200: mailing_response_get})
@swagger_auto_schema(method='post', request_body=MailingSerializer)
@api_view(['GET', 'POST'])
def api_mailing(request):
    if request.method == 'GET':
        mailing = Mailing.objects.all()
        serializer = MailingSerializer(mailing, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = MailingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            check_mailing(serializer.data['id'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={200: mailing_response_detail_get})
@swagger_auto_schema(methods=['put', 'patch'], request_body=MailingSerializer)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_mailing_detail(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'GET':
        return Response(MailingMessagesSerializer(mailing).data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = MailingSerializer(mailing, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        mailing.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='get', responses={200: mailing_statistics_response_get})
@api_view(['GET'])
def api_mailing_statistics(request):
    context = []
    mailings = Mailing.objects.all()

    for mailing in mailings:
        context.append(MailingMessagesSerializer(instance=mailing).data)

    return Response(context)


@api_view(['GET'])
def api_test(request):
    if request.method == 'GET':
        mailing = Mailing.objects.get(pk=10)
        clients = mailing.get_clients()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def api_send_created_messages(request):
    messages = Message.objects.filter(status=Message.Status.CREATED)
    for i in messages:
        send_message.delay(i.id,)
    return Response([], status=status.HTTP_200_OK)
