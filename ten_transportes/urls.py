from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),

    # Página de inicio
    path('', TemplateView.as_view(template_name='core/inicio.html'), name='inicio'),

    # 🔹 Incluye las rutas de la app usuarios
    path('usuarios/', include('usuarios.urls')),  

    # Páginas específicas
    path('cliente/', TemplateView.as_view(template_name='core/cliente.html'), name='cliente'),
    path('operador/', TemplateView.as_view(template_name='core/operador.html'), name='operador'),
    path('empresa/', TemplateView.as_view(template_name='core/empresa.html'), name='empresa'),
    path('administrador/', TemplateView.as_view(template_name='core/administrador.html'), name='administrador'),

    # Login y Logout (mantén estos, pero los moveremos luego a usuarios)
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='core/login.html'),
        name='login'
    ),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Registro (temporal, mientras configuramos en usuarios)
    path(
        'accounts/register/',
        CreateView.as_view(
            template_name='core/register.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('login')
        ),
        name='register'
    ),

    # Rutas de restablecimiento de contraseña
    path(
        'accounts/password_reset/',
        auth_views.PasswordResetView.as_view(template_name='core/password_reset_form.html'),
        name='password_reset'
    ),
    path(
        'accounts/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'accounts/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]
