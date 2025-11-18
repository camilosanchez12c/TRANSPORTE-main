from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_global, name='login'),
    path('registro_cliente/', views.registro_cliente, name='registro_cliente'),
]
