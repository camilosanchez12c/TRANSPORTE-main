# base/views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import datetime

# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

class HealthCheckView(APIView):
    """
    Endpoint de salud para la API (GET).
    Permite comprobar que la API está arriba: /api/health/  (o la ruta que configures)
    """
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        return Response({
            "status": "ok",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "message": "API lista"
        })

# @login_required : esto es para proteger la ruta para que solo usuarios verificados entren
def inicio(request):
    """
    Renderiza la página de inicio (landing).
    Asegúrate de tener templates/core/inicio.html
    """
    return render(request, 'core/inicio.html')
#este es para que en el login quede un registro al momento de presionar el boton de registrarse 
def register(request):
    # vista básica demostrativa — no es producción (no valida todo)
    if request.method == "POST":
        username = request.POST.get('username') or request.POST.get('email')
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Añadir validaciones reales en un proyecto real
        if username and password:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Cuenta creada. Ahora puedes iniciar sesión.")
            return redirect('login')  # o nombre de tu login
        else:
            messages.error(request, "Completa los campos requeridos.")
    return render(request, "core/register.html")
