# usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # LOGIN GLOBAL
    path('login/', views.login_global, name='login'),

    # REGISTROS
    path('register/cliente/', views.registro_cliente, name='registro_cliente'),
    path('register/empresa/', views.registro_empresa, name='registro_empresa'),
    path('register/operador/', views.registro_operador, name='registro_operador'),
    # LOGOUT
    path('logout/', views.logout_view, name='logout'),
    path("validar_email/", views.validar_email, name="validar_email"), 
]
