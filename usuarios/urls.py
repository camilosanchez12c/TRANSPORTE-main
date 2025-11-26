# usuarios/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'usuarios'

urlpatterns = [
    # LOGIN GLOBAL
    path('login/', views.login_global, name='login'),

    # REGISTROS
    path('register/cliente/', views.registro_cliente, name='registro_cliente'),
    path('register/empresa/', views.registro_empresa, name='registro_empresa'),
    path('register/operador/', views.registro_operador, name='registro_operador'),

    # LOGOUT
    path('logout/', views.logout_view, name='logout'),

    # Validar email
    path("validar_email/", views.validar_email, name="validar_email"),

    # RECUPERACIÓN DE CONTRASEÑA (password reset)
    path('password_reset/', auth_views.PasswordResetView.as_view(
            template_name='usuarios/password_reset_form.html',
            email_template_name='usuarios/password_reset_email.txt',
            subject_template_name='usuarios/password_reset_subject.txt',
            html_email_template_name='usuarios/password_reset_email_html.html',
        ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
            template_name='usuarios/password_reset_done.html'
        ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
            template_name='usuarios/password_reset_confirm.html'
        ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
            template_name='usuarios/password_reset_complete.html'
        ), name='password_reset_complete'),
]
