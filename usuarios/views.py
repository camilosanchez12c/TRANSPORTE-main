from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from django.http import JsonResponse
from .models import Usuario
from empresas.models import Empresa
from .forms import ClienteRegistroForm, RegistroEmpresaForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import re

# ============================================================
#  LOGIN GLOBAL PERSONALIZADO
# ============================================================

def login_global(request):

    errors = {}

    if request.method == "POST":
        
        
        
        email = request.POST.get("username").strip()
        password = request.POST.get("password")
        role = request.POST.get("role")

        roles_dict = {
            "cliente": 1,
            "empresa": 2,
            "operador": 3,
            "administrador": 4,
        }

        rol_id_esperado = roles_dict.get(role)

        # 1. ¿El correo existe?
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            errors["email"] = "El correo no está registrado."
            return render(request, "core/login.html", {"errors": errors})

        # 2. ¿El rol coincide?
        if usuario.rol_id != rol_id_esperado:
            errors["email"] = "Este usuario no pertenece al tipo seleccionado."
            return render(request, "core/login.html", {"errors": errors})

        # 3. ¿La contraseña es correcta?
        if not check_password(password, usuario.password):
            errors["password"] = "La contraseña es incorrecta."
            return render(request, "core/login.html", {"errors": errors})

        # 4. Estado
        if not usuario.is_active:
            errors["email"] = "Tu cuenta está desactivada."
            return render(request, "core/login.html", {"errors": errors})

        # LOGIN OK
        request.session["usuario_id"] = usuario.id_usuario
        request.session["usuario_nombre"] = usuario.nombre
        request.session["usuario_rol"] = usuario.rol_id

        if usuario.rol_id == 1:
            return redirect("cliente")
        elif usuario.rol_id == 2:
            return redirect("empresa")
        elif usuario.rol_id == 3:
            return redirect("operador")
        elif usuario.rol_id == 4:
            return redirect("administrador")

    return render(request, "core/login.html")
# ============================================================
#  REGISTRO CLIENTE
# ============================================================

def registro_cliente(request):
    if request.method == 'POST':
        form = ClienteRegistroForm(request.POST)
        if form.is_valid():

            if Usuario.objects.filter(email=form.cleaned_data['email']).exists():
                # añadir error al campo email y volver a mostrar el formulario
                form.add_error('email', "Este correo ya está registrado.")
                return render(request, 'core/registro_cliente.html', {'form': form})

            usuario = form.save(commit=False)
            usuario.password = make_password(form.cleaned_data['password'])
            usuario.rol_id = 1
            usuario.is_active = 1
            usuario.save()

            messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
            return redirect("login")
    else:
        form = ClienteRegistroForm()

    return render(request, 'core/registro_cliente.html', {'form': form})

#validaciones del perfil de cliente 
def login_view(request):
    if request.method == "POST":
        email = (request.POST.get("username") or "").strip()
        password = request.POST.get("password")
        role = request.POST.get("role")

        # VALIDACIONES BÁSICAS
        if not email or not password:
            messages.error(request, "Todos los campos son obligatorios.")
            # render (no redirect) para que el mensaje se muestre en la misma respuesta
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        if "@" not in email:
            messages.error(request, "El correo no es válido.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # verificar si existe el usuario (en tu caso tu modelo Usuario o User de Django)
        from usuarios.models import Usuario  # o ajusta la import si tu model está en otro módulo
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            messages.error(request, "Este correo no está registrado. Por favor regístrate.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # validar rol (según tu esquema)
        roles_dict = {"cliente": 1, "empresa": 2, "operador": 3, "administrador": 4}
        rol_id_esperado = roles_dict.get(role)
        if rol_id_esperado and usuario.rol_id != rol_id_esperado:
            messages.error(request, "Este usuario no pertenece al tipo seleccionado.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # validar contraseña (tu contraseña está hasheada con make_password)
        from django.contrib.auth.hashers import check_password
        if not check_password(password, usuario.password):
            messages.error(request, "La contraseña es incorrecta.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # validar estado
        if not usuario.is_active:
            messages.error(request, "Tu cuenta está desactivada. Contacta con soporte.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # LOGIN: guardar en sesión (tu implementación actual)
        request.session["usuario_id"] = usuario.id_usuario
        request.session["usuario_nombre"] = usuario.nombre
        request.session["usuario_rol"] = usuario.rol_id

        # redirigir según rol (ajusta nombres de url)
        if usuario.rol_id == 1:
            return redirect("cliente")
        if usuario.rol_id == 2:
            return redirect("empresa")
        if usuario.rol_id == 3:
            return redirect("operador")
        if usuario.rol_id == 4:
            return redirect("administrador")

        return redirect("inicio")

    # GET -> mostrar formulario
    return render(request, "core/login.html")

# ============================================================
#  REGISTRO EMPRESA
# ============================================================

def registro_empresa(request):
    if request.method == 'POST':
        form = RegistroEmpresaForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                with transaction.atomic():

                    # Crear usuario representante legal
                    usuario = Usuario.objects.create(
                        nombre=form.cleaned_data['nombre_representante'],
                        email=form.cleaned_data['email'],
                        telefono=form.cleaned_data['telefono'],
                        password=make_password(form.cleaned_data['password']),
                        rol_id=2,  # Empresa
                        is_active=1
                    )

                    # Crear empresa
                    Empresa.objects.create(
                        id_usuario=usuario,
                        nombre=form.cleaned_data['razon_social'],
                        nit=form.cleaned_data['nit'],
                        direccion=form.cleaned_data['direccion'],
                        ciudad=form.cleaned_data['ciudad'],
                        documento_rut=form.cleaned_data['rut'],
                        documento_camara=form.cleaned_data['camara_comercio'],
                        documento_operacion=form.cleaned_data['licencia_operacion'],
                        estado='pendiente'
                    )

                messages.success(request, "Registro completado. Tu empresa está en validación.")
                return redirect("login")

            except Exception as e:
                print("ERROR REGISTRO EMPRESA:", e)
                messages.error(request, "Error interno al registrar la empresa.")

    else:
        form = RegistroEmpresaForm()

    return render(request, 'core/registro_empresa.html', {"form": form})



# ============================================================
#  REGISTRO OPERADOR
# ============================================================

def registro_operador(request):
    if request.method == "POST":

        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('registro_operador')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Este correo ya está registrado.")
            return redirect('registro_operador')

        Usuario.objects.create(
            nombre=nombre,
            email=email,
            telefono=telefono,
            password=make_password(password),
            rol_id=3,  # Operador
            is_active=1
        )

        messages.success(request, "Operador registrado correctamente.")
        return redirect('login')

    return render(request, 'core/registro_operador.html')



# ============================================================
#  LOGOUT
# ============================================================

def logout_view(request):
    request.session.flush()  # limpia toda la sesión
    return redirect("login")

def validar_email(request):
    email = request.GET.get("email")
    existe = Usuario.objects.filter(email=email).exists()
    return JsonResponse({"existe": existe})


def cliente_view(request):
    return render(request, "core/cliente.html")

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from django.http import JsonResponse
from .models import Usuario
from empresas.models import Empresa
from .forms import ClienteRegistroForm, RegistroEmpresaForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import re

# ============================================================
#  LOGIN GLOBAL PERSONALIZADO
# ============================================================

def login_global(request):

    errors = {}

    if request.method == "POST":
        
        email = request.POST.get("username").strip()
        password = request.POST.get("password")
        role = request.POST.get("role")

        # ====================================================
        # 🌟 ADMINISTRADOR (usa auth_user de Django)
        # ====================================================
        if role == "administrador":

            # 1. Buscar usuario por email
            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                errors["email"] = "No existe un administrador con este correo."
                return render(request, "core/login.html", {"errors": errors})

            # 2. Autenticamos usando su username real
            user = authenticate(request, username=user_obj.username, password=password)

            if user is None:
                errors["password"] = "Contraseña incorrecta."
                return render(request, "core/login.html", {"errors": errors})

            # 3. Verificar permisos de admin
            if not user.is_superuser and not user.is_staff:
                errors["email"] = "Este usuario no tiene permisos de administrador."
                return render(request, "core/login.html", {"errors": errors})

            # 4. Login OK
            login(request, user)
            return redirect("administrador")

        # ====================================================
        # 🌟 OTROS ROLES -> tu tabla Usuario
        # ====================================================

        roles_dict = {
            "cliente": 1,
            "empresa": 2,
            "operador": 3,
        }

        rol_id_esperado = roles_dict.get(role)

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            errors["email"] = "El correo no está registrado."
            return render(request, "core/login.html", {"errors": errors})

        # validar rol
        if usuario.rol_id != rol_id_esperado:
            errors["email"] = "Este usuario no pertenece al tipo seleccionado."
            return render(request, "core/login.html", {"errors": errors})

        # validar contraseña
        if not check_password(password, usuario.password):
            errors["password"] = "La contraseña es incorrecta."
            return render(request, "core/login.html", {"errors": errors})

        # guardar sesión
        request.session["usuario_id"] = usuario.id_usuario
        request.session["usuario_nombre"] = usuario.nombre
        request.session["usuario_rol"] = usuario.rol_id

        # redirecciones
        if usuario.rol_id == 1:
            return redirect("cliente")
        elif usuario.rol_id == 2:
            return redirect("empresa")
        elif usuario.rol_id == 3:
            return redirect("operador")

    return render(request, "core/login.html")
# ============================================================
#  REGISTRO CLIENTE
# ============================================================

def registro_cliente(request):
    if request.method == 'POST':
        form = ClienteRegistroForm(request.POST)
        if form.is_valid():

            if Usuario.objects.filter(email=form.cleaned_data['email']).exists():
                # añadir error al campo email y volver a mostrar el formulario
                form.add_error('email', "Este correo ya está registrado.")
                return render(request, 'core/registro_cliente.html', {'form': form})

            usuario = form.save(commit=False)
            usuario.password = make_password(form.cleaned_data['password'])
            usuario.rol_id = 1
            usuario.is_active = 1
            usuario.save()

            messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
            return redirect("login")
    else:
        form = ClienteRegistroForm()

    return render(request, 'core/registro_cliente.html', {'form': form})

#validaciones del perfil de cliente 
def login_view(request):
    if request.method == "POST":
        email = (request.POST.get("username") or "").strip()
        password = request.POST.get("password")
        role = request.POST.get("role")

        # VALIDACIONES BÁSICAS
        if not email or not password:
            messages.error(request, "Todos los campos son obligatorios.")
            # render (no redirect) para que el mensaje se muestre en la misma respuesta
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        if "@" not in email:
            messages.error(request, "El correo no es válido.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # verificar si existe el usuario (en tu caso tu modelo Usuario o User de Django)
        from usuarios.models import Usuario  # o ajusta la import si tu model está en otro módulo
        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            messages.error(request, "Este correo no está registrado. Por favor regístrate.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # validar rol (según tu esquema)
        roles_dict = {"cliente": 1, "empresa": 2, "operador": 3, "administrador": 4}
        rol_id_esperado = roles_dict.get(role)
        if rol_id_esperado and usuario.rol_id != rol_id_esperado:
            messages.error(request, "Este usuario no pertenece al tipo seleccionado.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # validar contraseña (tu contraseña está hasheada con make_password)
        from django.contrib.auth.hashers import check_password
        if not check_password(password, usuario.password):
            messages.error(request, "La contraseña es incorrecta.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # validar estado
        if not usuario.is_active:
            messages.error(request, "Tu cuenta está desactivada. Contacta con soporte.")
            return render(request, "core/login.html", {"username": email, "role_selected": role})

        # LOGIN: guardar en sesión (tu implementación actual)
        request.session["usuario_id"] = usuario.id_usuario
        request.session["usuario_nombre"] = usuario.nombre
        request.session["usuario_rol"] = usuario.rol_id

        # redirigir según rol (ajusta nombres de url)
        if usuario.rol_id == 1:
            return redirect("cliente")
        if usuario.rol_id == 2:
            return redirect("empresa")
        if usuario.rol_id == 3:
            return redirect("operador")
        if usuario.rol_id == 4:
            return redirect("administrador")

        return redirect("inicio")

    # GET -> mostrar formulario
    return render(request, "core/login.html")

# ============================================================
#  REGISTRO EMPRESA
# ============================================================

def registro_empresa(request):
    if request.method == 'POST':
        form = RegistroEmpresaForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                with transaction.atomic():

                    # Crear usuario representante legal
                    usuario = Usuario.objects.create(
                        nombre=form.cleaned_data['nombre_representante'],
                        email=form.cleaned_data['email'],
                        telefono=form.cleaned_data['telefono'],
                        password=make_password(form.cleaned_data['password']),
                        rol_id=2,  # Empresa
                        is_active=1
                    )

                    # Crear empresa
                    Empresa.objects.create(
                        id_usuario=usuario,
                        nombre=form.cleaned_data['razon_social'],
                        nit=form.cleaned_data['nit'],
                        direccion=form.cleaned_data['direccion'],
                        ciudad=form.cleaned_data['ciudad'],
                        documento_rut=form.cleaned_data['rut'],
                        documento_camara=form.cleaned_data['camara_comercio'],
                        documento_operacion=form.cleaned_data['licencia_operacion'],
                        estado='pendiente'
                    )

                messages.success(request, "Registro completado. Tu empresa está en validación.")
                return redirect("login")

            except Exception as e:
                print("ERROR REGISTRO EMPRESA:", e)
                messages.error(request, "Error interno al registrar la empresa.")

    else:
        form = RegistroEmpresaForm()

    return render(request, 'core/registro_empresa.html', {"form": form})



# ============================================================
#  REGISTRO OPERADOR
# ============================================================

def registro_operador(request):
    if request.method == "POST":

        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('registro_operador')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Este correo ya está registrado.")
            return redirect('registro_operador')

        Usuario.objects.create(
            nombre=nombre,
            email=email,
            telefono=telefono,
            password=make_password(password),
            rol_id=3,  # Operador
            is_active=1
        )

        messages.success(request, "Operador registrado correctamente.")
        return redirect('login')

    return render(request, 'core/registro_operador.html')



# ============================================================
#  LOGOUT
# ============================================================

def logout_view(request):
    request.session.flush()  # limpia toda la sesión
    return redirect("login")

def validar_email(request):
    email = request.GET.get("email")
    existe = Usuario.objects.filter(email=email).exists()
    return JsonResponse({"existe": existe})


def cliente_view(request):
    return render(request, "core/cliente.html")
