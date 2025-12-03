# ten_transportes/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

# Importo la vista de login de tu app usuarios para crear un alias named 'login'
# Esto evita romper plantillas que usan {% url 'login' %}
from usuarios import views as usuarios_views

urlpatterns = [
    # ADMIN
    path('admin/', admin.site.urls),

    # RUTA GLOBAL 'login' (alias) para evitar NoReverseMatch en templates que usan {% url 'login' %}
    # Esto no elimina /accounts/login/ — solo crea una entrada adicional con name='login'.
    path('login/', usuarios_views.login_global, name='login'),

    # INICIO
    path('', TemplateView.as_view(template_name='core/inicio.html'), name='inicio'),

    # USUARIOS (login + registro + logout)
    # mantiene todas las rutas definidas en usuarios/urls.py bajo /accounts/
    path('accounts/', include('usuarios.urls')),

    # PÁGINAS DE ROLES
    path('cliente/', TemplateView.as_view(template_name='core/cliente.html'), name='cliente'),
    path('operador/', TemplateView.as_view(template_name='core/operador.html'), name='operador'),
    path('empresa/', TemplateView.as_view(template_name='core/empresa.html'), name='empresa'),
    path('administrador/', TemplateView.as_view(template_name='core/administrador.html'), name='administrador'),
    path('usuarios/', include('usuarios.urls')),
    path('operador/', include('operadores.urls')),

    # RECUPERACIÓN DE CONTRASEÑA (mantengo tus rutas existentes)
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='core/password_reset_form.html'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), name='password_reset_complete'),
    
]
