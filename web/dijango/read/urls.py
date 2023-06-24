from django.urls import path
from . import views

urlpatterns = [
    path('read/', views.hello),
]