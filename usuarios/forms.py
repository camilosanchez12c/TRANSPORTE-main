from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class ClienteRegistroForm(forms.ModelForm):
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput()
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'password', 'password2']
        error_messages = {
            'email': {
                'unique': "Este correo ya está registrado.",
            }
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password2')

        if p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden")

        return cleaned_data
    def clean_telefono(self):
        tel = self.cleaned_data.get('telefono', '')
        digits = ''.join(filter(str.isdigit, tel))
        if len(digits) != 10:
            raise forms.ValidationError("El teléfono debe tener exactamente 10 dígitos.")
        return digits
    
class RegistroEmpresaForm(forms.Form):

    # Datos del representante
    nombre_representante = forms.CharField(max_length=100)
    email = forms.EmailField()
    telefono = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    # Datos de la empresa
    razon_social = forms.CharField(max_length=255)
    nit = forms.CharField(max_length=50)
    direccion = forms.CharField(max_length=255)
    ciudad = forms.CharField(max_length=100)

    # Documentos
    rut = forms.FileField()
    camara_comercio = forms.FileField()
    licencia_operacion = forms.FileField()

    def clean(self):
        cleaned = super().clean()

        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned