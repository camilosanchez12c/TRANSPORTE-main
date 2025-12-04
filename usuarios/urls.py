# usuarios/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'usuarios'

urlpatterns = [

    # login y registros
    path('login/', views.login_global, name='login'),
    path('register/cliente/', views.registro_cliente, name='registro_cliente'),
    path('register/empresa/', views.registro_empresa, name='registro_empresa'),
    path('register/operador/', views.registro_operador, name='registro_operador'),

    # logout
    path('logout/', views.logout_view, name='logout'),

    # recuperar contraseña (custom + admin)
    path('recuperar/', views.recuperar_contrasena_correo, name='recuperar_contrasena_correo'),
    path("reset-password/", views.reset_password, name="reset_password"),

    # admin (built-in con tus templates)
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="usuarios/password_reset_form.html",
            email_template_name="usuarios/password_reset_email.txt",
            html_email_template_name="usuarios/password_reset_email_html.html",
            subject_template_name="usuarios/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="usuarios/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="usuarios/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="usuarios/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path('cambiar-contrasena-perfil/', views.cambiar_contrasena_desde_perfil, name='cambiar_contrasena_desde_perfil'),
path('perfil-operador/', views.perfil_operador, name='perfil_operador'),
path("perfil-cliente/", views.perfil_cliente, name="perfil_cliente"),

]
