from django.urls import path
from .api import views

urlpatterns = [
    path('test/', views.test_api, name='test_api'),
]