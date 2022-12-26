from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Client, Mailing
from .serializers import MailingSerializer, ClientSerializer, MessageSerializer

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

test_param = openapi.Parameter('client_id', openapi.IN_PATH, description="test manual param",
                               required=True, type=openapi.FORMAT_INT64)

response_400 = openapi.Response('BAD_REQUEST')

mailing_statistics = openapi.Schema(
    title='mailing statistics list',
    description='mailing list with information about messages',
    type=openapi.TYPE_ARRAY,
    items=openapi.Schema(
        title='Mailing info',
        description='Mailing info with messages',
        type=openapi.TYPE_OBJECT,
        properties={'id': {'type': 'integer'}},
    )
)

client_response_get = openapi.Response('Client list', ClientSerializer(many=True))
client_response_post = openapi.Response('New Client', ClientSerializer)
client_response_detail_get = openapi.Response('Client object', ClientSerializer)

mailing_response_get = openapi.Response('Mailing list', MailingSerializer(many=True))
mailing_response_post = openapi.Response('New Mailing', MailingSerializer)
mailing_statistics = openapi.Response('Mailing statistics', mailing_statistics)


@swagger_auto_schema(method='get', responses={200: client_response_get})
@swagger_auto_schema(method='post', responses={200: client_response_post, 400: response_400})
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
@swagger_auto_schema(method='post', responses={200: mailing_response_post, 400: response_400})
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_mailing_detail(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'GET':
        return Response(get_mailing_context(mailing))
    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = MailingSerializer(mailing, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        mailing.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method='get', responses={200: mailing_statistics})
@api_view(['GET'])
def api_mailing_statistics(requests):
    context = []
    mailings = Mailing.objects.all()

    for mailing in mailings:
        context.append(get_mailing_context(mailing))

    return Response(context)


# business logic
def get_mailing_context(mailing: Mailing):
    context = MailingSerializer(mailing).data
    messages_all = mailing.message_mailing.all()
    context['messages'] = {
        'created': MessageSerializer(messages_all.filter(status='c'), many=True).data,
        'shipped': MessageSerializer(messages_all.filter(status='s'), many=True).data,
        'delivered': MessageSerializer(messages_all.filter(status='d'), many=True).data,
    }
    return context

