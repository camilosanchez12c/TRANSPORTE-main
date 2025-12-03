from django.urls import path
from . import views

urlpatterns = [
    path("perfil/", views.perfil_operador, name="perfil_operador"),
]
