from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class ClienteRegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'direccion', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'cliente'  # el registro crea solo clientes
        if commit:
            user.save()
        return user
