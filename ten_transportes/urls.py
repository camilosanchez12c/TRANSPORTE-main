from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ADMIN
    path('admin/', admin.site.urls),

    # INICIO
    path('', TemplateView.as_view(template_name='core/inicio.html'), name='inicio'),

    # USUARIOS (login + registro + logout)
    path('accounts/', include('usuarios.urls')),

    # PÁGINAS DE ROLES
    path('cliente/', TemplateView.as_view(template_name='core/cliente.html'), name='cliente'),
    path('operador/', TemplateView.as_view(template_name='core/operador.html'), name='operador'),
    path('empresa/', TemplateView.as_view(template_name='core/empresa.html'), name='empresa'),
    path('administrador/', TemplateView.as_view(template_name='core/administrador.html'), name='administrador'),
    
    # RECUPERACIÓN DE CONTRASEÑA
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='core/password_reset_form.html'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), name='password_reset_complete'),
]
