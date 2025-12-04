# ten_transportes/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

# Para usar el login global de la app usuarios
from usuarios import views as usuarios_views

urlpatterns = [
    # ----------------------------------------
    # ADMIN
    # ----------------------------------------
    path('admin/', admin.site.urls),

    # ----------------------------------------
    # LOGIN GLOBAL (alias para evitar NoReverseMatch)
    # ----------------------------------------
    path('login/', usuarios_views.login_global, name='login'),

    # ----------------------------------------
    # INICIO
    # ----------------------------------------
    path('', TemplateView.as_view(
        template_name='core/inicio.html'), name='inicio'),

    # ----------------------------------------
    # APP USUARIOS (login, registro, logout...)
    # ----------------------------------------
    # Todas las rutas de usuarios dentro de /accounts/
    path('accounts/', include('usuarios.urls')),

    # ----------------------------------------
    # PÁGINAS DE ROLES
    # ----------------------------------------
    path('cliente/', TemplateView.as_view(
        template_name='core/cliente.html'), name='cliente'),

    path('operador-panel/', TemplateView.as_view(
        template_name='core/operador.html'), name='operador'),

    path('empresa/', TemplateView.as_view(
        template_name='core/empresa.html'), name='empresa'),

    path('administrador/', TemplateView.as_view(
        template_name='core/administrador.html'), name='administrador'),

    # ----------------------------------------
    # APP OPERADORES
    # ----------------------------------------
    path('operador/', include('operadores.urls')),

    # ----------------------------------------
    # RECUPERACIÓN DE CONTRASEÑA (Django)
    # - AHORA usando tus templates reales en /templates/usuarios/
    # ----------------------------------------
    path(
        'accounts/password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='usuarios/password_reset_form.html',
            email_template_name='usuarios/password_reset_email.txt',
            subject_template_name='usuarios/password_reset_subject.txt',
            html_email_template_name='usuarios/password_reset_email_html.html',
        ),
        name='password_reset'
    ),

    path(
        'accounts/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='usuarios/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='usuarios/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'accounts/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='usuarios/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
