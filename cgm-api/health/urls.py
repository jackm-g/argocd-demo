from django.urls import path
from . import views

urlpatterns = [
    path('live', views.liveness_check, name='liveness'),
    path('ready', views.readiness_check, name='readiness'),
]

