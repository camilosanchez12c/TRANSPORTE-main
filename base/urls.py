from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
]
