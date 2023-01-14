from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'service'

urlpatterns = [
    path('docs/', TemplateView.as_view(
        template_name='swagger-ui.html',
    ), name='swagger-ui'),
    path('api/client/<int:pk>/', views.api_client_detail),
    path('api/client/', views.api_client),
    path('api/mailing/<int:pk>/', views.api_mailing_detail),
    path('api/mailing/send/', views.api_send_created_messages),
    path('api/mailing/statistics/', views.api_mailing_statistics),
    path('api/mailing/', views.api_mailing),
    path('celery/message/', views.celery_callback),
    path('test/', views.api_test),
]
