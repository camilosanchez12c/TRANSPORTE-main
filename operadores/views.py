from django.shortcuts import render, redirect
from django.contrib import messages
from usuarios.models import Usuario


def perfil_operador(request):

    # 1. Validar si hay sesión activa
    operador_id = request.session.get("usuario_id")
    operador_rol = request.session.get("usuario_rol")

    if not operador_id:
        messages.error(request, "Debes iniciar sesión primero.")
        return redirect("login")

    # 2. Verificar que el rol sea operador (rol_id = 3)
    if operador_rol != 3:
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect("login")

    # 3. Obtener datos del operador
    try:
        operador = Usuario.objects.get(id_usuario=operador_id)
    except Usuario.DoesNotExist:
        messages.error(request, "El usuario no existe.")
        return redirect("login")

    # 4. Renderizar el perfil del operador
    return render(request, "operadores/perfil_operador.html", {
        "operador": operador
    })
