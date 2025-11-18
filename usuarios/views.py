from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import ClienteRegistroForm
from .models import Usuario
from django.contrib.auth.decorators import login_required

# LOGIN GLOBAL
def login_global(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')  # viene del template

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Si es admin, no se necesita role manual, pero igual se revisa
            if user.rol == 'administrador' or user.rol == role:
                login(request, user)
                if user.rol == 'cliente':
                    return redirect('cliente')
                elif user.rol == 'empresa':
                    return redirect('empresa')
                elif user.rol == 'operador':
                    return redirect('operador')
                elif user.rol == 'administrador':
                    return redirect('administrador')
                else:
                    return redirect('inicio')
            else:
                messages.error(request, "Rol incorrecto para este usuario.")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, 'core/login.html')


# REGISTRO CLIENTE
def registro_cliente(request):
    if request.method == 'POST':
        form = ClienteRegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
            return redirect('login')
    else:
        form = ClienteRegistroForm()

    return render(request, 'core/register_cliente.html', {'form': form})
